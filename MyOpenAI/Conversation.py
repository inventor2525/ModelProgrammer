import sqlite3
import hashlib
import json

import datetime
from typing import List, Dict

get_hash = lambda x: hashlib.sha256(str(x).encode("utf-8")).hexdigest()

class Message():
	def __init__(self, data:Dict[str, str], date=None):
		self.json = data
		if date is None:
			if "created" in data:
				self.date = datetime.datetime.fromtimestamp(int(data["created"]))
			else:
				self.date = datetime.datetime.now()
		self.hash = get_hash(json.dumps(self.json))
	
	@classmethod
	def from_role_content(cls, role:str, content:str):
		if role in ["user", "assistant", "system"]:
			return cls({"role":role, "content":content})
		else:
			return cls({"role":"user", "name":role, "content":content})
	
	def __str__(self):
		return json.dumps(self.json)
		
	def __getitem__(self, key):
		return self.json[key]

class Conversation():
	def __init__(self, messages:List[Message]):
		self.messages = messages
		self.hash = ""
		self._recompute_hash()
	
	@property
	def hashes(self):
		"""
		Get the hashes of all messages in the conversation.
		"""
		return [message.hash for message in self.messages]
		
	def _recompute_hash(self):
		self.hash = get_hash(self.hashes)
	
	@classmethod
	def from_list(cls, messages:List[Dict[str, str]]):
		return cls([Message(message) for message in messages])
		
	def as_list(self):
		"""
		Generates a sendable list of messages jsons ready to be sent to OpenAI's Chat API.
		
		Returns:
			list: A list of message dictionaries, each of which has a "role" key and a "content" key, some also have a "name" key.
		"""
		return [message.json for message in self.messages]
	
	def add_message(self, message:Message):
		self.messages.append(message)
		self._recompute_hash()
		
	def __str__(self):
		return json.dumps([str(message) for message in self.messages])