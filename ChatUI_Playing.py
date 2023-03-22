from MyOpenAI.ChatUI import *
from MyOpenAI.Conversation import *
from MyOpenAI.ConversationDB import *
from MyOpenAI.ChatBot import *

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
		self.chat_ui.show()
	
	def message_changed(self, message:Message, old_hash:str):
		self.db.save_message(message, MessageType.Edit, old_hash)
	
	def message_added(self, conversation:Conversation, message:Message, should_send:bool):
		self.db.save_message(message, MessageType.ManualEntry)
		if len(conversation.messages)>0:
			self.db.save_conversation(conversation)
		
		if message is not None:
			conversation.add_message(message)
		
		self.db.save_conversation(conversation)
		
		response = None
		if should_send:
			if message is None or message.full_role != "assistant":
				response_json = asyncio.run(self.programmer.send_conversation(conversation))
				response = Message(response_json)
				self.db.save_response_for_conversation(conversation, response) #Save the raw response from the chatbot
				response = self.format_response(response) #Format the response as a Message supported by the ChatUI and ChatBot
				self.db.save_message(response, MessageType.FormatedChatbotResponse, response.hash) #Save the formated response refering to the raw response
				
				self.chat_ui.render_message(response)
				conversation.add_message(response)
				self.db.save_conversation(conversation)
		elif message is not None and message.full_role == "assistant":
				response = message
		
		if response is not None:
			#TODO: parse out the command(s) from the response and run them
			terminal_output = asyncio.run(self.terminal.run_command(response.content, 2))
			output_message = Message.from_role_content("terminal", terminal_output)
			self.db.save_message(output_message, MessageType.TerminalOutput)
			self.conversation.add_message(output_message)
			self.db.save_conversation(self.conversation)
			self.chat_ui.render_message(output_message)
			
	def format_response(self, response:Message) -> Message:
		if response is None:
			return None
		content = response.json["choices"][0]["message"]["content"]
		return Message.from_role_content("assistant", content)		
	
if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	db = ConversationDB("Programmer_v0.db")
	conversation = db.load_conversation(db.latest_conversation)
	programmer = Programmer(db, conversation)
	
	sys.exit(app.exec_())
