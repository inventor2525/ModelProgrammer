import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea, QLabel
from .Conversation import Conversation, Message

class ChatUI(QWidget):
	def __init__(self, conversation: Conversation):
		super().__init__()

		self.setWindowTitle('Chatbot')
		self.setGeometry(100, 100, 600, 400)

		main_layout = QVBoxLayout()

		self.chat_log = QVBoxLayout()

		self.scroll_area = QScrollArea()
		scroll_widget = QWidget()
		scroll_widget.setLayout(self.chat_log)
		self.scroll_area.setWidget(scroll_widget)
		self.scroll_area.setWidgetResizable(True)

		main_layout.addWidget(self.scroll_area)

		input_layout = QHBoxLayout()

		self.input_box = QLineEdit()
		input_layout.addWidget(self.input_box)

		send_button = QPushButton('Send')
		send_button.clicked.connect(self.send_message)
		input_layout.addWidget(send_button)

		main_layout.addLayout(input_layout)
		self.setLayout(main_layout)
		
		self.conversation = conversation
		for message in self.conversation.messages:
			self.add_message(message["role"], message.json.get("name","name N/A"), message["content"])

	def send_message(self):
		message = self.input_box.text().strip()
		if message:
			self.add_message('user', 'User', message)
			self.input_box.clear()
			response = self.get_chatbot_response(message)
			self.add_message('assistant', 'Chatbot', response)

	def add_message(self, role, name, message):
		message_label = QLabel(f'<b>{role.capitalize()} ({name}):</b> {message}')
		self.chat_log.addWidget(message_label)

	def get_chatbot_response(self, message):
		# Replace this function with your actual chatbot function
		return "This is the AI response."
