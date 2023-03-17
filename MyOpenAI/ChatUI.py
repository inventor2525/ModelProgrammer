import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea, QLabel
from .Conversation import Conversation, Message
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFrame, QAbstractItemView
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSizePolicy, QToolButton
from PyQt5.QtCore import Qt, QSize, QPoint, QSettings, QByteArray, pyqtSignal, QRect
from PyQt5.QtGui import QIcon, QPixmap, QImage, QTextOption, QColor, QPalette, QPainter

class ColoredFrame(QFrame):
	def __init__(self, background_color, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.background_color = background_color
		self.selected = False

	def paintEvent(self, event):
		if not self.selected:
			painter = QPainter(self)
			painter.fillRect(QRect(0, 0, self.width(), self.height()), self.background_color)
			
		super().paintEvent(event)

	def set_selected(self, selected):
		self.selected = selected
		self.update()
		
class MessageView(ColoredFrame):
	rowHeightChanged = pyqtSignal()
	
	def __init__(self, message: Message, parent=None):
		background_color = QColor( parent.color_palette.get(message.full_role.lower(), QColor(Qt.white)) )
		super().__init__(background_color, parent)
		
		self.parent = parent
		self.list_view = parent.list_view
		#self.setAutoFillBackground(True)
		self.message = message

		# rowHeightChanged = pyqtSignal()
		
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)
		
		self.color_palette = parent.color_palette

		# Set background color for the row
		# background_color = self.color_palette.get(message.full_role, QColor(Qt.green))
		
		# self.set_widget_background(self, background_color)
		
		# self.setAutoFillBackground(True)
		# palette = self.palette()
		# palette.setColor(QPalette.Background, background_color)
		# self.setPalette(palette)

		# Role (and optional name) label
		self.role_label = QLabel()
		self.role_label.setText(f"{message.full_role}:")
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
		self.text_edit.textChanged.connect(self.update_text_edit_height)
		self.layout.addWidget(self.text_edit)

		# Vertical panel
		self.panel_layout = QVBoxLayout()
		self.panel_layout.setAlignment(Qt.AlignTop)
		self.layout.addLayout(self.panel_layout)

		# Delete button (X)
		self.delete_btn = QPushButton("X")
		self.delete_btn.clicked.connect(self.delete_message)
		self.delete_btn.setFixedWidth(25)
		self.panel_layout.addWidget(self.delete_btn, alignment=Qt.AlignTop)
		self.delete_btn.clicked.connect(lambda: self.parent.delete_message(self))
		
		# Confirm button (checkmark)
		self.confirm_btn = QPushButton("✓")
		self.confirm_btn.clicked.connect(self.confirm_changes)
		self.confirm_btn.setVisible(False)
		self.confirm_btn.setFixedWidth(25)
		self.panel_layout.addWidget(self.confirm_btn, alignment=Qt.AlignTop)

		# Expand message view button (rotating arrow)
		self.expand_btn = QToolButton()
		self.expand_btn.setCheckable(True)
		self.expand_btn.setArrowType(Qt.RightArrow)
		self.expand_btn.toggled.connect(self.toggle_expand)
		self.panel_layout.addWidget(self.expand_btn, alignment=Qt.AlignTop)

		self.update_text_edit_height()
	
	def update_text_edit_height(self):
		new_height = int(self.delete_btn.sizeHint().height() * 3)
		margins = self.text_edit.contentsMargins()
		if self.expand_btn.arrowType() == Qt.DownArrow:
			new_height = max(int(self.text_edit.document().size().height()), new_height) + margins.top() + margins.bottom()
			self.text_edit.setFixedHeight(new_height)
		else:
			new_height = int(self.delete_btn.sizeHint().height() * 3) + margins.top() + margins.bottom()
			self.text_edit.setFixedHeight(new_height)
		self.rowHeightChanged.emit()
		
	def toggle_expand(self, checked):
		self.expand_btn.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
		self.update_text_edit_height()
		
	def on_text_changed(self):
		if self.text_edit.toPlainText() != self.message['content']:
			self.confirm_btn.setVisible(True)
			# self.text_edit.setStyleSheet("border: 3px solid rgba(0, 0, 255, 0.3);")
			self.text_edit.setStyleSheet("QTextEdit {border: 3px solid rgba(0, 0, 255, 0.3);}")

		else:
			self.confirm_btn.setVisible(False)
			self.text_edit.setStyleSheet("")
			
		if self.expand_btn.isChecked():
			self.text_edit.setMinimumHeight(int(self.text_edit.document().size().height()))
			self.text_edit.updateGeometry()
			self.rowHeightChanged.emit()
		
	def delete_message(self):
		pass

	def confirm_changes(self):
		pass


class ChatUI(QWidget):
	def __init__(self, conversation: Conversation, max_new_message_lines=5):
		super().__init__()
		self.colors = QColor.colorNames()#  ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'gray']
		
		self._color_palette = {
			"system": "lightgrey",
			"user human": "#9DFFA6",
			"user terminal": "#FFEBE4",
			"assistant": "#FFC4B0",
		}
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
		self.list_view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
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
		
		self.list_view.itemSelectionChanged.connect(self.update_selection)

	def update_selection(self):
		for index in range(self.list_view.count()):
			item = self.list_view.item(index)
			message_view = self.list_view.itemWidget(item)
			message_view.set_selected(item.isSelected())
		
	def read_settings(self):
		settings = QSettings("MyCompany", "MyApp")
		self.restoreGeometry(settings.value("geometry", QByteArray()))

	def write_settings(self):
		settings = QSettings("MyCompany", "MyApp")
		settings.setValue("geometry", self.saveGeometry())
	
	@property
	def color_palette(self):
		if not hasattr(self, '_color_palette') or self._color_palette is None:
			self._color_palette = {}
			message_types = set()

			# Extract message types from the messages in the conversation
			for message in self.conversation.messages:
				message_types.add(message.full_role.lower())

			# Assign colors to message types
			for i, message_type in enumerate(sorted(message_types)):
				message_type = message_type.lower()
				self._color_palette[message_type] = self.colors[i % len(self.colors)]

		return self._color_palette


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
			
	def delete_message(self, message_widget):
		if message_widget is not None:
			item = None
			for index in range(self.list_view.count()):
				current_item = self.list_view.item(index)
				if self.list_view.itemWidget(current_item) == message_widget:
					item = current_item
					break

			if item is not None:
				row = self.list_view.row(item)
				item = self.list_view.takeItem(row)

				message_to_remove = message_widget.message
				self.conversation.messages.remove(message_to_remove)
				
				self.list_view.clearSelection()

		
	def update_row_height(self, item: QListWidgetItem):
		item_widget = self.list_view.itemWidget(item)
		item.setSizeHint(QSize(item_widget.sizeHint().width(), item_widget.sizeHint().height()))
		
	def add_message(self, message: Message):
		message_type = message.full_role.lower()
		if message_type not in self.color_palette:
			self._color_palette[message_type] = self.colors[len(self._color_palette) % len(self.colors)]
			
		# self.conversation.add_message(message)
		item = QListWidgetItem()
		item_widget = MessageView(message, self)
		item_widget.rowHeightChanged.connect(lambda: self.update_row_height(item))
		item.setSizeHint(item_widget.sizeHint())
		self.list_view.addItem(item)
		self.list_view.setItemWidget(item, item_widget)
		self.list_view.scrollToBottom()
		
	def closeEvent(self, event):
		self.write_settings()
		super().closeEvent(event)
		
	def keyPressEvent(self, event):
		item_widget = self.list_view.itemWidget(self.list_view.currentItem())
		if event.key() == Qt.Key_Delete and not item_widget.text_edit.hasFocus():
			#if selection is not empty, delete all selected messages
			if self.list_view.selectedItems():
				for item in self.list_view.selectedItems():
					item_widget = self.list_view.itemWidget(item)
					self.delete_message(item_widget)
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

		if n_lines >= self.max_new_message_lines:
			self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		else:
			self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
			
		self.input_field.updateGeometry()
		
		if self.num_lines < n_lines:
			self.input_field.verticalScrollBar().setValue(self.input_field.verticalScrollBar().maximum())
		self.num_lines = n_lines