import openai
import sqlite3
import hashlib
import json
import datetime

previous_chat = None
def chat(messages, model="gpt-3.5-turbo", temperature=0):
	"""
	1. Hashes each message and saves it uniquely to a sqlite database by its hash.
	2. Records in a seperate table the list of hashes that make up this conversation.
	3. Sends the messages to OpenAI's Chat API.
	4. Saves the response to the database by its hash, and records the hash in the conversation table.
	5. Returns a response from OpenAI's Chat API.
	
	Note that all hashes are SHA-256 hashes.
	
	Args:
		messages (list): A list of dictionaries, each of which has a "role" key and a "content" key.
		model (str): The model to use. Defaults to "gpt-3.5-turbo".
		temperature (float): The temperature to use. Defaults to 0.
		
	Returns:
		dict: A dictionary containing the response from OpenAI's Chat API.
	"""
	global previous_chat
	get_hash = lambda x: hashlib.sha256(str(x).encode("utf-8")).hexdigest()
	
	#Hash the messages
	hashes = []
	for message in messages:
		hashes.append(get_hash(message))
		
	#Save the hashes to a sqlite database, ensuring that the database exists if it hasn't been created yet.
	conn = sqlite3.connect("Chatter.db")
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS messages (hash text, json text, PRIMARY KEY (hash))")
	c.execute("CREATE TABLE IF NOT EXISTS message_info (hash text, role text, source text, datetime text, PRIMARY KEY (hash))")
	c.execute("CREATE TABLE IF NOT EXISTS conversations (hash text, previous_conversation text, message_hashes text, response_hashs text, PRIMARY KEY (hash))")
	
	#Get the datetime in 2023-01-01 00:00:00 format
	date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	
	#Save the messages to the database
	for message, hash in zip(messages, hashes):
		#Save the message to the database preserving the origional message if it exists
		c.execute("SELECT * FROM messages WHERE hash = ?", (hash,))
		if not c.fetchone():
			c.execute("INSERT INTO messages VALUES (?, ?)", (hash, json.dumps(message)))
		
		#Save the message_info to the database preserving the origional info if it exists
		c.execute("SELECT * FROM message_info WHERE hash = ?", (hash,))
		if not c.fetchone():
			c.execute("INSERT INTO message_info VALUES (?, ?, ?, ?)", (hash, message["role"], "chat param", date))
	
	#Save the conversation to the database if it doesn't already exist
	chat_hash = get_hash(hashes)
	c.execute("SELECT * FROM conversations WHERE hash = ?", (chat_hash,))
	if not c.fetchone():
		c.execute("INSERT INTO conversations VALUES (?, ?, ?, ?)", (chat_hash, previous_chat, json.dumps(hashes), None))
	previous_chat = chat_hash
	
	#Commit the changes to the database
	conn.commit()
	
	#Send the messages to OpenAI's Chat API
	pre_response_time = datetime.datetime.now()
	response = openai.ChatCompletion.create(
		model=model,
		messages=messages,
		temperature=temperature,
		max_tokens=300,
	)
	
	#print how long it's been in seconds since the request was sent, with a helpful message
	print(f"OpenAI's Chat API took {datetime.datetime.now() - pre_response_time} seconds to respond.")
	date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	
	#Save the response to the database
	response_hash = get_hash(response)
	c.execute("INSERT INTO messages VALUES (?, ?)", (response_hash, json.dumps(response)))
	conn.commit()
	
	#Save the message_info to the database preserving the origional info if it exists
	c.execute("SELECT * FROM message_info WHERE hash = ?", (response_hash,))
	if not c.fetchone():
		c.execute("INSERT INTO message_info VALUES (?, ?, ?, ?)", (response_hash, "assistant", "OpenAI Chat API", date))
	
	print(response)
	#Update the conversation to include the response by first getting the response_hashs
	c.execute("SELECT response_hashs FROM conversations WHERE hash = ?", (chat_hash,))
	#parse the response_hashs from the database handling the fact that it may be None
	fetched_result = c.fetchone()
	if fetched_result is None or fetched_result[0] is None:
		response_hashs = []
	else:
		response_hashs = json.loads(fetched_result[0])
	#update the response_hashs for the conversation
	c.execute("UPDATE conversations SET response_hashs = ? WHERE hash = ?", (json.dumps(response_hashs + [response_hash]), chat_hash))
	
	#Commit the changes to the database, close the connection, and return the response
	conn.commit()
	conn.close()
	
	return response