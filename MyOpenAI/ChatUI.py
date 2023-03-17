import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea, QLabel
from .Conversation import Conversation, Message
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFrame
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSizePolicy, QToolButton
from PyQt5.QtCore import Qt, QSize, QPoint, QSettings, QByteArray
from PyQt5.QtGui import QIcon, QPixmap, QImage, QTextOption

class MessageView(QFrame):
	def __init__(self, message: Message, parent=None):
		super().__init__(parent)
		self.parent = parent
		self.list_view = parent.list_view
		
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
		self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
		self.text_edit.textChanged.connect(self.on_text_changed)
		
		self.layout.addWidget(self.text_edit)

		# Vertical panel
		self.panel_layout = QVBoxLayout()
		self.layout.addLayout(self.panel_layout)

		# Delete button (X)
		self.delete_btn = QPushButton("X")
		self.delete_btn.clicked.connect(self.delete_message)
		self.delete_btn.setFixedWidth(25)
		self.panel_layout.addWidget(self.delete_btn, alignment=Qt.AlignTop)

		# Confirm button (checkmark)
		self.confirm_btn = QPushButton("✓")
		self.confirm_btn.clicked.connect(self.confirm_changes)
		self.confirm_btn.setVisible(False)
		self.confirm_btn.setFixedWidth(25)
		self.panel_layout.addWidget(self.confirm_btn)

		# Expand message view button (rotating arrow)
		self.expand_btn = QToolButton()
		self.expand_btn.setCheckable(True)
		self.expand_btn.setArrowType(Qt.RightArrow)
		self.expand_btn.toggled.connect(self.toggle_expand)
		self.panel_layout.addWidget(self.expand_btn, alignment=Qt.AlignBottom)

	def toggle_expand(self, checked):
		if checked:
			self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
			self.text_edit.setMinimumHeight(int(self.text_edit.document().size().height()))
			self.expand_btn.setArrowType(Qt.DownArrow)
		else:
			self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
			self.text_edit.setMaximumHeight(int(self.delete_btn.sizeHint().height() * 3))
			self.expand_btn.setArrowType(Qt.RightArrow)
		self.text_edit.updateGeometry()
		
	def on_text_changed(self):
		if self.text_edit.toPlainText() != self.message['content']:
			self.confirm_btn.setVisible(True)
			self.text_edit.setStyleSheet("border: 3px solid rgba(0, 0, 255, 0.3);")
		else:
			self.confirm_btn.setVisible(False)
			self.text_edit.setStyleSheet("")
		
	def delete_message(self):
		pass

	def confirm_changes(self):
		pass


class ChatUI(QWidget):
	def __init__(self, conversation: Conversation, max_new_message_lines=5):
		super().__init__()

		self.conversation = conversation
		self.max_new_message_lines = max_new_message_lines
		self.init_ui()
		for message in conversation.messages:
			self.add_message(message)
		
		self.read_settings()
		self.num_lines = 0

	def init_ui(self):
		self.setWindowTitle('Chat')

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.list_view = QListWidget()
		self.list_view.setAutoScroll(False)
		self.layout.addWidget(self.list_view)
		
		self.input_layout = QHBoxLayout()

		self.input_field = QTextEdit()
		size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
		size_policy.setVerticalStretch(1)
		self.input_field.setSizePolicy(size_policy)
		self.input_field.setMaximumHeight(self.input_field.fontMetrics().lineSpacing())
		self.input_field.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
		self.input_field.textChanged.connect(self.adjust_input_field_size)
		self.input_field.setPlaceholderText("Type your message here...")
		self.input_layout.addWidget(self.input_field)

		self.send_button = QPushButton('Send')
		self.send_button.clicked.connect(self.send_message)
		self.input_layout.addWidget(self.send_button, alignment=Qt.AlignBottom)
		
		self.layout.addLayout(self.input_layout)
		self.input_field.setMinimumHeight(self.send_button.sizeHint().height())

		
	def read_settings(self):
		settings = QSettings("MyCompany", "MyApp")
		self.restoreGeometry(settings.value("geometry", QByteArray()))

	def write_settings(self):
		settings = QSettings("MyCompany", "MyApp")
		settings.setValue("geometry", self.saveGeometry())
		
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
			
	def delete_message(self):
		row = self.list_view.currentRow()
		item = self.list_view.takeItem(row)

		message_widget = item.data(Qt.UserRole)
		message_to_remove = message_widget.message
		self.conversation.messages.remove(message_to_remove)
		
		self.list_view.clearSelection()
		
	def add_message(self, message: Message):
		# self.conversation.add_message(message)
		item = QListWidgetItem()
		item_widget = MessageView(message, self)
		item_widget.delete_btn.clicked.connect(self.delete_message)
		item.setSizeHint(item_widget.sizeHint())
		self.list_view.addItem(item)
		self.list_view.setItemWidget(item, item_widget)
		self.list_view.scrollToBottom()
		
	def closeEvent(self, event):
		self.write_settings()
		super().closeEvent(event)
		
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Delete and not self.list_view.itemWidget(self.list_view.currentItem()).text_edit.hasFocus():
			self.delete_message()
		elif event.key() == Qt.Key_Enter and event.modifiers() == Qt.ControlModifier:
			self.send_button.click()
		else:
			super().keyPressEvent(event)
			
	def adjust_input_field_size(self):
		"""Adjust the height of the input field to fit the text up to max lines"""
		n_lines = self.input_field.document().blockCount()
		lines_to_show = min(n_lines, self.max_new_message_lines)
		new_height = self.input_field.fontMetrics().lineSpacing() * lines_to_show + 10
		self.input_field.setMaximumHeight(int(new_height))
		
		 # Adjust the height of the rows in the message view
		for i in range(self.list_view.count()):
			item = self.list_view.item(i)
			item_widget = self.list_view.itemWidget(item)
			item.setSizeHint(QSize(item_widget.sizeHint().width(), item_widget.sizeHint().height()))

		if n_lines >= self.max_new_message_lines:
			self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		else:
			self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
			
		self.input_field.updateGeometry()
		
		if self.num_lines < n_lines:
			self.input_field.verticalScrollBar().setValue(self.input_field.verticalScrollBar().maximum())
		self.num_lines = n_lines