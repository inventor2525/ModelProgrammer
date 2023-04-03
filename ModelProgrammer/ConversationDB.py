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
			"source_hash_id": ("INTEGER", None),
		}

		conversations_columns = {
			"id": ("INTEGER PRIMARY KEY", None),
			"hash": ("TEXT", None),
			"datetime": ("TEXT", None),
			"version": ("INTEGER", None),
			"description": ("TEXT NOT NULL", ''),
			"startup_script": ("TEXT NOT NULL", ''),
			"source_hash_id": ("INTEGER", None),
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

		# Get the source message id if the source hash is provided
		source_message_id = None
		if source_hash:
			self.cursor.execute("SELECT id FROM messages WHERE hash = ?", (source_hash,))
			source_message_id = self.cursor.fetchone()
			if source_message_id:
				source_message_id = source_message_id[0]

		# Check if the message exists in the database
		self.cursor.execute("SELECT id FROM messages WHERE hash = ?", (message.hash,))
		existing_message = self.cursor.fetchone()

		if existing_message:
			message_id = existing_message[0]
		else:
			# If the message does not exist, insert it
			self.cursor.execute("""
				INSERT INTO messages (hash, content, datetime, type, role, source_hash_id)
				VALUES (?, ?, ?, ?, ?, ?)
			""", (message.hash, str(message), date, int(message_type), message.full_role, source_message_id))
			message_id = self.cursor.lastrowid

		self.connection.commit()
		return message_id
				
	def save_conversation(self, conversation: Conversation, source_hash:Optional[str] = None) -> int:
		"""
		Saves a conversation to the database.
		"""
		date = self.now()

		# Get the source conversation id if the source hash is provided
		source_conversation_id = None
		if source_hash:
			self.cursor.execute("SELECT id FROM conversations WHERE hash = ?", (source_hash,))
			source_conversation_id = self.cursor.fetchone()
			if source_conversation_id:
				source_conversation_id = source_conversation_id[0]

		# Check if the conversation exists in the database
		self.cursor.execute("SELECT id FROM conversations WHERE hash = ?", (conversation.hash,))
		existing_conversation = self.cursor.fetchone()

		if existing_conversation:
			conversation_id = existing_conversation[0]
		else:
			# If the conversation does not exist, insert it
			self.cursor.execute("""
				INSERT INTO conversations (hash, datetime, description, startup_script, source_hash_id)
				VALUES (?, ?, ?, ?, ?)
			""", (conversation.hash, date, '', '', source_conversation_id))
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
		
		old_hash = conversation.hash
		conversation.add_message(response)
		self.save_conversation(conversation, old_hash)

		self.connection.commit()

	@property
	def latest_conversation(self) -> Optional[str]:
		self.cursor.execute("SELECT hash FROM conversations ORDER BY datetime DESC LIMIT 1")
		row = self.cursor.fetchone()
		if row is None:
			return None
		return row[0]

	def load_message(self, message_hash: str) -> Optional[Message]:
		self.cursor.execute("SELECT content, role FROM messages WHERE hash = ?", (message_hash,))
		row = self.cursor.fetchone()
		if row is None:
			return None
		message_content, full_role = row
		message_dict = json.loads(message_content)
		return Message.from_role_content(full_role, message_dict["content"])
		
	def load_conversation(self, conversation_hash: str) -> Optional[Conversation]:
		self.cursor.execute("SELECT id, datetime FROM conversations WHERE hash = ?", (conversation_hash,))
		row = self.cursor.fetchone()
		if row is None:
			return None

		conversation_id, datetime = row
		self.cursor.execute("SELECT message_id FROM conversation_messages WHERE conversation_id = ? ORDER BY message_order", (conversation_id,))
		message_ids = [row[0] for row in self.cursor.fetchall()]

		messages = [self.load_message_by_id(message_id) for message_id in message_ids]
		return Conversation(messages)

	def load_message_by_id(self, message_id: int) -> Optional[Message]:
		self.cursor.execute("SELECT hash FROM messages WHERE id = ?", (message_id,))
		message_hash = self.cursor.fetchone()[0]
		if message_hash is None:
			return None
		return self.load_message(message_hash)
	   
	def get_conversation_description(self, conversation: Conversation) -> str:
		self.cursor.execute("SELECT description FROM conversations WHERE hash = ?", (conversation.hash,))
		description = self.cursor.fetchone()
		return description[0] if description else ""

	def set_conversation_description(self, conversation: Conversation, description: str):
		self.save_conversation(conversation)
		self.cursor.execute("UPDATE conversations SET description = ? WHERE hash = ?", (description, conversation.hash,))
		self.connection.commit()

	def get_conversation_startup_script(self, conversation: Conversation) -> str:
		self.cursor.execute("SELECT startup_script FROM conversations WHERE hash = ?", (conversation.hash,))
		startup_script = self.cursor.fetchone()
		return startup_script[0] if startup_script else ""

	def set_conversation_startup_script(self, conversation: Conversation, startup_script: str):
		self.save_conversation(conversation)
		self.cursor.execute("UPDATE conversations SET startup_script = ? WHERE hash = ?", (startup_script, conversation.hash,))
		self.connection.commit()