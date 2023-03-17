import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea, QLabel
from .Conversation import Conversation, Message
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFrame
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSizePolicy, QToolButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QImage, QTextOption

class MessageView(QFrame):
    def __init__(self, message: Message):
        super().__init__()

        self.message = message

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Role (and optional name) label
        self.role_label = QLabel()
        if 'name' in message.json:
            self.role_label.setText(f"{message['role']} ({message['name']}):")
        else:
            self.role_label.setText(f"{message['role']}:")
        self.role_label.setFixedWidth(100)
        self.role_label.setWordWrap(True)
        self.layout.addWidget(self.role_label)

        # Editable text box
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(message['content'])
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(self.text_edit)

        # Expand message view button
        self.expand_btn = QToolButton()
        self.expand_btn.setCheckable(True)
        self.expand_btn.setIcon(QIcon(QPixmap.fromImage(QImage("path/to/triangle_icon.png")))) # Replace with the actual path to the triangle icon
        self.expand_btn.toggled.connect(self.toggle_expand)
        self.layout.addWidget(self.expand_btn)

    def toggle_expand(self, checked):
        if checked:
            self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.expand_btn.setArrowType(Qt.DownArrow)
        else:
            self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.expand_btn.setArrowType(Qt.RightArrow)
        self.text_edit.updateGeometry()


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
