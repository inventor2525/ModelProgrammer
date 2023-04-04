from ModelProgrammer.ChatUI import *
from ModelProgrammer.Conversation import *
from ModelProgrammer.ConversationDB import *
from ModelProgrammer.ChatBot import *

class Programmer():
	def __init__(self, db:ConversationDB, conversation:Conversation=None, terminal:Terminal=None):
		if conversation is None:
			conversation = Conversation([])
		if terminal is None:
			terminal = Terminal()
		
		self.db = db
		self.conversation = conversation
		self.terminal = terminal
		
		self.programmer = ChatBot()
		
		self.chat_ui = ChatUI(conversation, [
			"Assistant",
			"System",
			"User",
			"Terminal",
			"Human"
		])
		self.chat_ui.message_changed.connect(self.message_changed)
		self.chat_ui.message_added.connect(self.message_added)
		self.chat_ui.confirm_command.connect(self.run_terminal_command)
		self.chat_ui.show()
	
	def message_changed(self, message:Message, old_hash:str):
		self.db.save_message(message, MessageType.Edit, old_hash)
	
	def message_added(self, conversation:Conversation, message:Message, should_send:bool):		
		if message is not None and len(message.content)>0:
			self.db.save_message(message, MessageType.ManualEntry)
			self.chat_ui.render_message(message)
			if len(conversation.messages)>0:
				self.db.save_conversation(conversation)
				
			conversation.add_message(message)
		
		self.db.save_conversation(conversation)
		
		response = None
		if should_send:
			if message is None or message.full_role != "assistant":
				response_json = None
				try:
					response_json = asyncio.run(self.programmer.send_conversation(conversation))
				except Exception as e:
					print(e)
					
				if response_json is not None:
					response = Message(response_json)
					self.db.save_message(response, MessageType.RawChatbotResponse) #Save the raw response from the chatbot
					raw_response_hash = response.hash
					
					response = self.format_response(response) #Format the response as a Message supported by the ChatUI and ChatBot
					self.db.save_message(response, MessageType.FormattedChatbotResponse, raw_response_hash) #Save the formatted response referring to the raw response
					
					conversation.add_message(response)
					self.db.save_conversation(conversation)
					
					self.chat_ui.render_message(response)
					self.chat_ui.has_unrun_command = True #TODO: check if the response contains a command
		elif message is not None and message.full_role == "assistant":
			response = message
			self.chat_ui.has_unrun_command = True #TODO: check if the response contains a command
		
		#TODO: parse out the command(s) from the response and run them
		self.response = response
	
	def run_terminal_command(self):
		if self.response is None or self.chat_ui.has_unrun_command == False:
			return
		self.chat_ui.has_unrun_command = False
		terminal_output = asyncio.run(self.terminal.run_command(self.response.content, 2))
		output_message = Message.from_role_content("terminal", terminal_output)
		self.db.save_message(output_message, MessageType.TerminalOutput)
		self.conversation.add_message(output_message)
		self.db.save_conversation(self.conversation)
		self.chat_ui.render_message(output_message)
		self.chat_ui.update_send_button_text()
		
	def format_response(self, response:Message) -> Message:
		if response is None:
			return None
		content = response.json["choices"][0]["message"]["content"]
		return Message.from_role_content("assistant", content)