import sqlite3
import hashlib
import json

import datetime
from typing import List, Dict

class Hashable():
	def __init__(self):
		self.hash = ""
	
	def recompute_hash(self):
		raise NotImplementedError()
		
	def _compute_hash(self, x:object) -> str:
		return hashlib.sha256(str(x).encode("utf-8")).hexdigest()
		
class Message(Hashable):
	def __init__(self, data:Dict[str, str], date=None):
		self.json = data
		if date is None:
			if "created" in data:
				self.date = datetime.datetime.fromtimestamp(int(data["created"]))
			else:
				self.date = datetime.datetime.now()
		self.recompute_hash()
		
	def recompute_hash(self) -> str:
		self.hash = self._compute_hash(json.dumps(self.json))
	
	@classmethod
	def from_role_content(cls, role:str, content:str):
		role = role.lower()
		if role in ["user", "assistant", "system"]:
			return cls({"role":role, "content":content})
		else:
			return cls({"role":"user", "name":role, "content":content})
	
	@property
	def full_role(self):
		if "role" not in self.json:
			return None
		role = self.json['role']
		if 'name' in self.json:
			return f"{role} {self.json['name']}".strip()
		return role.strip()
	
	@property
	def short_role(self):
		if 'name' in self.json:
			return self.json['name']
		else:
			return self.json['role']
	
	@property
	def content(self):
		if 'content' in self.json:
			return self.json['content']
		else:
			if 'choices' in self.json:
				return self.json['choices'][0]['message']['content']
		return None
	@content.setter
	def content(self, value):
		if 'content' in self.json:
			self.json['content'] = value
		else:
			if 'choices' in self.json:
				self.json['choices'][0]['message']['content'] = value
		
	def __str__(self):
		return json.dumps(self.json)
		
	def __getitem__(self, key):
		return self.json.get(key, None)

class Conversation(Hashable):
	def __init__(self, messages:List[Message]):
		self.messages = messages
		self.hash = ""
		self.recompute_hash()
	
	@property
	def hashes(self):
		"""
		Get the hashes of all messages in the conversation.
		"""
		return [message.hash for message in self.messages]
		
	def recompute_hash(self):
		self.hash = self._compute_hash(self.hashes)
	
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
		self.recompute_hash()
		
	def __str__(self):
		return json.dumps([str(message) for message in self.messages])