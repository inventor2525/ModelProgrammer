import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea, QLabel
from .Conversation import Conversation, Message
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFrame
from PyQt5.QtCore import Qt

class MessageView(QFrame):
	def __init__(self, message: Message):
		super().__init__()

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.label = QLabel()
		self.label.setText(f"{message['role']}: {message['content']}")
		self.label.setWordWrap(True)
		self.layout.addWidget(self.label)

class ChatUI(QWidget):
	def __init__(self, conversation: Conversation):
		super().__init__()

		self.conversation = conversation
		self.init_ui()
		for message in conversation.messages:
			self.add_message(message)

	def init_ui(self):
		self.setWindowTitle('Chat')

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.list_view = QListWidget()
		self.layout.addWidget(self.list_view)

		self.input_field = QLineEdit()
		self.input_field.setPlaceholderText("Type your message here...")
		self.input_field.returnPressed.connect(self.send_message)
		self.layout.addWidget(self.input_field)

	def send_message(self):
		message_text = self.input_field.text().strip()
		if message_text:
			message = Message.from_role_content("user", message_text)
			self.add_message(message)
			self.input_field.clear()

			# Handle response from the chat bot and render the assistant's message
			# Here's a placeholder example:
			response_text = "Assistant's response to: " + message_text
			response = Message.from_role_content("assistant", response_text)
			self.add_message(response)

	def add_message(self, message: Message):
		# self.conversation.add_message(message)
		item = QListWidgetItem()
		item_widget = MessageView(message)
		item.setSizeHint(item_widget.sizeHint())
		self.list_view.addItem(item)
		self.list_view.setItemWidget(item, item_widget)
		self.list_view.scrollToBottom()
