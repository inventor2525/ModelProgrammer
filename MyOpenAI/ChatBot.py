from MyOpenAI.Conversation import Conversation, Message
from MyOpenAI.Terminal import Terminal
from typing import List, Dict
import tiktoken
import asyncio
import json

import openai
import datetime

class ChatBot:
	def __init__(self, model="gpt-3.5-turbo", temperature=0):
		self.terminal = Terminal()
		self.model = model
		self.temperature = temperature
		
	async def handle_response(self, chat_bot_response: str) -> str:
		response_data = json.loads(chat_bot_response)
		message_content = response_data["choices"][0]["message"]["content"]
		command = message_content.replace(r'\n', '\n')
		terminal_output = await self.terminal.run_command(command)
		return terminal_output
	
	def count_conversation_tokens(self, conversation:Conversation) -> int:
		def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
			"""Returns the number of tokens used by a list of messages."""
			try:
				encoding = tiktoken.encoding_for_model(self.model)
			except KeyError:
				encoding = tiktoken.get_encoding("cl100k_base")
			if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
				num_tokens = 0
				for message in messages:
					num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
					for key, value in message.items():
						num_tokens += len(encoding.encode(value))
						if key == "name":  # if there's a name, the role is omitted
							num_tokens += -1  # role is always required and always 1 token
				num_tokens += 2  # every reply is primed with <im_start>assistant
				return num_tokens
			else:
				raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
		See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
		return num_tokens_from_messages(conversation.as_list())
		
	def count_message_tokens(self, message: str) -> int:
		encoding = tiktoken.encoding_for_model(self.model)
		tokens = encoding.encode(message)
		return len(tokens)
		
	#send_messages using the chat function from MyOpenAI/Chatter.py and return json
	async def send_conversation(self, conversation:Conversation, max_tokens:int=150) -> Dict[str,str]:
		conversation_tokens = self.count_conversation_tokens(conversation)
		max_tokens = min(4096 - conversation_tokens, max_tokens)
		if max_tokens < 0: #TODO: get this limit per model type
			raise ValueError(f"Conversation is too long for model {self.model} at {conversation_tokens} tokens, only 4096 are supported.")
		
		#Send the messages to OpenAI's Chat API
		pre_response_time = datetime.datetime.now()
		response = openai.ChatCompletion.create(
			model=self.model,
			messages=conversation.as_list(),
			temperature=self.temperature,
			max_tokens=max_tokens,
		)
		
		#print how long it's been in seconds since the request was sent, with a helpful message
		print(f"OpenAI's Chat API took {datetime.datetime.now() - pre_response_time} seconds to respond.")
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		
		return response