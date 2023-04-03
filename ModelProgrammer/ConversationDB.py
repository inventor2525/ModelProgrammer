from ModelProgrammer.Conversation import *
from typing import Optional
from enum import Enum
import datetime
import sqlite3
import hashlib
import json

class MessageType(Enum):
	RawChatbotResponse = 0
	FormattedChatbotResponse = 1
	ManualEntry = 2
	TerminalOutput = 3
	Edit = 4
	Unknown = 5

	def __int__(self):
		return self.value
	
def create_or_update_table(cursor, table_name, columns):
    # Create the table if it does not exist
    columns_definition = ', '.join([f"{col} {col_type}{f' DEFAULT {default!r}' if default is not None else ''}" for col, (col_type, default) in columns.items()])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})")

    # Check existing columns in the table
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {col_info[1]: col_info for col_info in cursor.fetchall()}

    # Add missing columns with default values
    for col, (col_type, default) in columns.items():
        if col not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type}{f' DEFAULT {default!r}' if default is not None else ''}")

class ConversationDB():
	"""
	Stores conversations in a sqlite database.
	
	Hashes each message and saves it uniquely to a sqlite database by its hash.
	Records in a separate table the list of message hashes that make up each conversation.
	Saves responses to the database by its hash, and records the hash in the conversation table.
	
	Note that all hashes are SHA-256 hashes.
	"""
	def __init__(self, path:str="Chatter.db"):
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()

		messages_columns = {
			"id": ("INTEGER PRIMARY KEY", None),
			"hash": ("TEXT", None),
			"content": ("TEXT", None),
			"datetime": ("TEXT", None),
			"type": ("INTEGER", None),
			"role": ("TEXT", None),
			"version": ("INTEGER", None),
		}

		conversations_columns = {
			"id": ("INTEGER PRIMARY KEY", None),
			"hash": ("TEXT", None),
			"datetime": ("TEXT", None),
			"version": ("INTEGER", None),
			"description": ("TEXT NOT NULL", ''),
			"startup_script": ("TEXT NOT NULL", ''),
		}

		conversation_messages_columns = {
			"conversation_id": ("INTEGER", None),
			"message_id": ("INTEGER", None),
			"message_order": ("INTEGER", None),
		}

		create_or_update_table(self.cursor, "messages", messages_columns)
		create_or_update_table(self.cursor, "conversations", conversations_columns)
		create_or_update_table(self.cursor, "conversation_messages", conversation_messages_columns)

		self.cursor.execute("""
			CREATE INDEX IF NOT EXISTS idx_conversations_hash ON conversations (hash)
		""")

		self.cursor.execute("""
			CREATE INDEX IF NOT EXISTS idx_messages_hash ON messages (hash)
		""")

		self.connection.commit()
	
	def now(self) -> str:
		'''Get the datetime in the format: 2023-01-01 00:00:00'''
		return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
	def save_message(self, message:Message, message_type:MessageType, source_hash: Optional[str] = None) -> int:
		"""
		Saves a message to the database.
		"""
		date = self.now()

		# Check if the message exists in the database
		self.cursor.execute("SELECT id, version FROM messages WHERE hash = ?", (message.hash,))
		existing_message = self.cursor.fetchone()

		if existing_message:
			message_id, version = existing_message
		else:
			# If the message does not exist, insert it and set version to 1
			version = 1
			self.cursor.execute("""
				INSERT INTO messages (hash, content, datetime, type, role, version)
				VALUES (?, ?, ?, ?, ?, ?)
			""", (message.hash, str(message), date, int(message_type), message.full_role, version))
			message_id = self.cursor.lastrowid

		self.connection.commit()
		return message_id
				
	def save_conversation(self, conversation: Conversation) -> int:
		"""
		Saves a conversation to the database.
		"""
		date = self.now()
		
		# Check if the conversation exists in the database
		self.cursor.execute("SELECT id, version FROM conversations WHERE hash = ?", (conversation.hash,))
		existing_conversation = self.cursor.fetchone()

		if existing_conversation:
			conversation_id, version = existing_conversation
		else:
			# If the conversation does not exist, insert it and set version to 1
			version = 1
			self.cursor.execute("""
				INSERT INTO conversations (hash, datetime, version)
				VALUES (?, ?, ?)
			""", (conversation.hash, date, version))
			conversation_id = self.cursor.lastrowid

		# Save messages and update conversation_messages
		message_order = 0
		for message in conversation.messages:
			message_id = self.save_message(message, MessageType.Unknown, conversation.hash)
			self.cursor.execute("""
				INSERT OR REPLACE INTO conversation_messages (conversation_id, message_id, message_order)
				VALUES (?, ?, ?)
			""", (conversation_id, message_id, message_order))
			message_order += 1

		self.connection.commit()
		return conversation_id
	
	def save_response_for_conversation(self, conversation:Conversation, response:Message):
		"""
		Saves a response to the database for the given conversation.
		"""
		date = self.now()
		conversation_id = self.save_conversation(conversation)
		message_id = self.save_message(response, MessageType.RawChatbotResponse, conversation.hash)

		# Add the response to the conversation_messages table
		self.cursor.execute("""
			INSERT INTO conversation_messages (conversation_id, message_id, message_order)
			VALUES (?, ?, (SELECT COALESCE(MAX(message_order), -1) + 1 FROM conversation_messages WHERE conversation_id = ?))
		""", (conversation_id, message_id, conversation_id))

		self.connection.commit()

	@property
	def latest_conversation(self) -> Optional[str]:
		self.cursor.execute("SELECT hash FROM conversations ORDER BY datetime DESC LIMIT 1")
		row = self.cursor.fetchone()
		if row is None:
			return None
		return row[0]

	def load_message(self, message_hash: str) -> Optional[Message]:
		self.cursor.execute("SELECT content FROM messages WHERE hash = ?", (message_hash,))
		message_text = self.cursor.fetchone()
		if message_text is None:
			return None
		message_dict = json.loads(message_text[0])
		return Message.from_role_content(message_dict["role"], message_dict["content"])
		
	def load_conversation(self, conversation_hash:str) -> Optional[Conversation]:
		self.cursor.execute("SELECT id FROM conversations WHERE hash = ?", (conversation_hash,))
		conversation_id = self.cursor.fetchone()

		if conversation_id is None:
			return None

		self.cursor.execute("""
			SELECT m.content
			FROM conversation_messages cm
			JOIN messages m ON cm.message_id = m.id
			WHERE cm.conversation_id = ?
			ORDER BY cm.message_order
		""", (conversation_id[0],))

		messages_dicts = [json.loads(message[0]) for message in self.cursor.fetchall()]
		messages = [Message.from_role_content(message["role"], message["content"]) for message in messages_dicts]

		return Conversation(messages)
	   
