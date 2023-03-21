from MyOpenAI.Conversation import *
from enum import Enum
import datetime
import sqlite3
import hashlib
import json

class MessageType(Enum):
	RawChatbotResponse = 0
	FormatedChatbotResponse = 1
	ManualEntry = 2
	TerminalOutput = 3
	Edit = 4
	Unknown = 5

	def __int__(self):
		return self.value
	
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
		self.cursor.execute("CREATE TABLE IF NOT EXISTS message_info (hash text, datetime text, type integer, role text, source_hash text, PRIMARY KEY (hash))")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS conversations (hash text, datetime text, message_hashes text, PRIMARY KEY (hash))")
		self.connection.commit()
	
	def now(self) -> str:
		'''Get the datetime in 2023-01-01 00:00:00 format'''
		return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
	def save_message(self, message:Message, message_type:MessageType, source_hash:str=None):
		"""
		Saves a message to the database.
		"""
		date = self.now()
		
		#Save the message to the database preserving the origional message if it exists
		self.cursor.execute("SELECT * FROM messages WHERE hash = ?", (message.hash,))
		if not self.cursor.fetchone():
			self.cursor.execute("INSERT INTO messages VALUES (?, ?)", (message.hash, str(message)))
		
		#Save the message_info to the database preserving the origional info if it exists
		self.cursor.execute("SELECT * FROM message_info WHERE hash = ?", (message.hash,))
		if not self.cursor.fetchone():
			self.cursor.execute("INSERT INTO message_info VALUES (?, ?, ?, ?, ?)", (message.hash, date, int(message_type), message.full_role, source_hash))
		self.connection.commit()
				
	def save_conversation(self, conversation:Conversation):
		"""
		Saves a conversation to the database.
		"""
		date = self.now()
		
		#Save the messages to the database
		for message in conversation.messages:
			self.save_message(message, MessageType.Unknown, conversation.hash)
		
		#Save the conversation to the database if it doesn't already exist
		self.cursor.execute("SELECT * FROM conversations WHERE hash = ?", (conversation.hash,))
		if not self.cursor.fetchone():
			self.cursor.execute("INSERT INTO conversations VALUES (?, ?, ?)", (conversation.hash, date, json.dumps(conversation.hashes)))
		
		#Commit the changes to the database
		self.connection.commit()
	
	# save a response from a chatbot to the database for the given conversation
	def save_response_for_conversation(self, conversation:Conversation, response:Message):
		"""
		Saves a response to the database for the given conversation.
		"""
		date = self.now()
		
		#Save the response to the database
		self.cursor.execute("INSERT INTO messages VALUES (?, ?)", (response.hash, json.dumps(response.json)))
		self.connection.commit()
		
		#Save the message_info to the database preserving the origional info if it exists
		self.cursor.execute("SELECT * FROM message_info WHERE hash = ?", (response.hash,))
		if not self.cursor.fetchone():
			self.cursor.execute("INSERT INTO message_info VALUES (?, ?, ?, ?, ?)", (response.hash, date, int(MessageType.RawChatbotResponse), "assistant", conversation.hash))
		self.connection.commit()
		
		#Commit the changes to the database
		self.connection.commit()