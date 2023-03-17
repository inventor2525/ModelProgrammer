from MyOpenAI.Conversation import *

class ConversationDB():
	"""
	Stores conversations in a sqlite database.
	
	Hashes each message and saves it uniquely to a sqlite database by its hash.
	Records in a seperate table the list of message hashes that make up each conversation.
	Saves responses to the database by its hash, and records the hash in the conversation table.
	
	Note that all hashes are SHA-256 hashes.
	"""
	def __init__(self, path:str="Chatter.db"):
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()
		self.cursor.execute("CREATE TABLE IF NOT EXISTS messages (hash text, json text, PRIMARY KEY (hash))")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS message_info (hash text, role text, source text, datetime text, PRIMARY KEY (hash))")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS conversations (hash text, previous_conversation text, message_hashes text, response_hashs text, PRIMARY KEY (hash))")
		self.connection.commit()
	
	def save_conversation(self, conversation:Conversation):
		"""
		Saves a conversation to the database.
		"""
		#Get the datetime in 2023-01-01 00:00:00 format
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
		#Save the messages to the database
		for message in conversation.messages:
			#Save the message to the database preserving the origional message if it exists
			self.cursor.execute("SELECT * FROM messages WHERE hash = ?", (message.hash,))
			if not self.cursor.fetchone():
				self.cursor.execute("INSERT INTO messages VALUES (?, ?)", (message.hash, str(message)))
			
			#Save the message_info to the database preserving the origional info if it exists
			self.cursor.execute("SELECT * FROM message_info WHERE hash = ?", (message.hash,))
			if not self.cursor.fetchone():
				self.cursor.execute("INSERT INTO message_info VALUES (?, ?, ?, ?)", (message.hash, message["role"], "chat param", date))
		
		#Save the conversation to the database if it doesn't already exist
		self.cursor.execute("SELECT * FROM conversations WHERE hash = ?", (conversation.hash,))
		if not self.cursor.fetchone():
			self.cursor.execute("INSERT INTO conversations VALUES (?, ?, ?, ?)", (conversation.hash, None, json.dumps(conversation.hashes), None))
		
		#Commit the changes to the database
		self.connection.commit()
	
	# save a response from a chatbot to the database for the given conversation
	def save_response_for_conversation(self, conversation:Conversation, response:Dict[str, str]):
		"""
		Saves a response to the database for the given conversation.
		"""
		#Get the datetime in 2023-01-01 00:00:00 format
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
		#Save the response to the database
		response_hash = get_hash(response)
		self.cursor.execute("INSERT INTO messages VALUES (?, ?)", (response_hash, json.dumps(response)))
		self.connection.commit()
		
		#Save the message_info to the database preserving the origional info if it exists
		self.cursor.execute("SELECT * FROM message_info WHERE hash = ?", (response_hash,))
		if not self.cursor.fetchone():
			self.cursor.execute("INSERT INTO message_info VALUES (?, ?, ?, ?)", (response_hash, "assistant", "OpenAI Chat API", date))
		
		#Update the conversation to include the response by first getting the response_hashs
		self.cursor.execute("SELECT response_hashs FROM conversations WHERE hash = ?", (conversation.hash,))
		#parse the response_hashs from the database handling the fact that it may be None
		fetched_result = self.cursor.fetchone()
		if fetched_result is None or fetched_result[0] is None:
			response_hashs = []
		else:
			response_hashs = json.loads(fetched_result[0])
		#update the response_hashs for the conversation
		self.cursor.execute("UPDATE conversations SET response_hashs = ? WHERE hash = ?", (json.dumps(response_hashs + [response_hash]), conversation.hash))
		
		#Commit the changes to the database
		self.connection.commit()