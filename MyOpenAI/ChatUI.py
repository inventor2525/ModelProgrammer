import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea, QLabel
from .Conversation import Conversation, Message
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QFrame, QAbstractItemView
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QFrame, QCheckBox, QVBoxLayout, QHBoxLayout, QCompleter, QLabel, QComboBox, QTextEdit, QSizePolicy, QToolButton
from PyQt5.QtCore import Qt, QSize, QPoint, QSettings, QByteArray, pyqtSignal, QRect
from PyQt5.QtGui import QIcon, QPixmap, QImage, QTextOption, QColor, QPalette, QPainter
from typing import Dict, List, Tuple, Optional, Union, Callable, Any

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
	message_changed = pyqtSignal(Message, str) # Message, old hash
	
	def __init__(self, message: Message, parent=None):
		background_color = QColor( parent.color_palette.get(message.full_role.lower(), QColor(Qt.white)) )
		super().__init__(background_color, parent)
		
		self.parent = parent
		self.message = message
		
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

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
		old_hash = self.message.hash
		self.message.json['content'] = self.text_edit.toPlainText()
		self.confirm_btn.setVisible(False)
		self.text_edit.setStyleSheet("")
		self.message.recompute_hash()
		
		self.message_changed.emit(self.message, old_hash)

class ConversationView(QListWidget):
	message_changed = pyqtSignal(Message, str) # Message, old hash
	
	def __init__(self, conversation: Conversation, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.colors = QColor.colorNames()#  ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'gray']
		
		self._color_palette = {
			"system": "lightgrey",
			"user human": "#9DFFA6",
			"user terminal": "#FFEBE4",
			"assistant": "#FFC4B0",
		}
		
		self.conversation = conversation
		
		for message in conversation.messages:
			self.render_message(message)
			
		self.setAutoScroll(False)
		self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.itemSelectionChanged.connect(self.update_selection)
	
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
		
	def update_selection(self):
		for index in range(self.count()):
			item = self.item(index)
			message_view = self.itemWidget(item)
			if message_view is not None:
				message_view.set_selected(item.isSelected())
	
	def keyPressEvent(self, event):
		item_widget = self.itemWidget(self.currentItem())
		if event.key() == Qt.Key_Delete and not item_widget.text_edit.hasFocus():
			#if selection is not empty, delete all selected messages
			if self.selectedItems():
				for item in self.selectedItems():
					item_widget = self.itemWidget(item)
					self.delete_message(item_widget)
		elif event.key() == Qt.Key_Escape:
			self.clearSelection()
		else:
			super().keyPressEvent(event)
	
	def delete_message(self, message_widget): #TODO: this needs to take a message not a widget
		if message_widget is not None:
			item = None
			for index in range(self.count()):
				current_item = self.item(index)
				if self.itemWidget(current_item) == message_widget:
					item = current_item
					break

			if item is not None:
				row = self.row(item)
				item = self.takeItem(row)

				message_to_remove = message_widget.message
				self.conversation.messages.remove(message_to_remove)
				
				self.clearSelection()
	
	def render_message(self, message: Message):
		message_type = message.full_role.lower()
		if message_type not in self.color_palette:
			self._color_palette[message_type] = self.colors[len(self._color_palette) % len(self.colors)]
			
		item = QListWidgetItem()
		item_widget = MessageView(message, self)
		item_widget.rowHeightChanged.connect(lambda: self.update_row_height(item))
		def message_changed(message: Message, old_hash: str):
			self.message_changed.emit(message, old_hash)
			self.conversation.recompute_hash()
			self.update_row_height(item)
		item_widget.message_changed.connect(message_changed)
		item.setSizeHint(item_widget.sizeHint())
		self.addItem(item)
		self.setItemWidget(item, item_widget)
		self.scrollToBottom()
				
	def add_message(self, message: Message):
		self.conversation.add_message(message)
		self.render_message(message)
		
	def update_row_height(self, item: QListWidgetItem):
		item_widget = self.itemWidget(item)
		item.setSizeHint(QSize(item_widget.sizeHint().width(), item_widget.sizeHint().height()))

class RoleComboBox(QComboBox):
	def __init__(self, values:List[str], default_value:str="Human", *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setEditable(True)
		self.default_value = default_value
		self.addItems(values)
		self.set_default_value()
		#do not auto complete
		self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion)
		self.setInsertPolicy(QComboBox.NoInsert)
		
	def set_default_value(self):
		index = self.findText(self.default_value)
		if index != -1:
			self.setCurrentIndex(index)
			
class ChatUI(QWidget):
	#qt signal for sending messages
	message_added = pyqtSignal(Conversation, Message, bool)
	message_changed = pyqtSignal(Message, str) # Message, old hash
	confirm_command = pyqtSignal()
	
	def __init__(self, conversation: Conversation, roles:List[str], max_new_message_lines=5):
		super().__init__()
		
		self.conversation = conversation
		self.roles = roles
		
		self.max_new_message_lines = max_new_message_lines
		self.num_lines = 0
		
		self.init_ui()
		self.has_unrun_command = False
		
		self.read_settings()
		
	def init_ui(self):
		self.setWindowTitle('Chat')

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)

		self.list_view = ConversationView(self.conversation)
		self.list_view.message_changed.connect(self.message_changed.emit)
		self.layout.addWidget(self.list_view)
		
		self.input_layout = QHBoxLayout()
		self.role_combobox = RoleComboBox(self.roles, default_value="Human")
		self.input_layout.addWidget(self.role_combobox, alignment=Qt.AlignBottom)

		self.input_field = QTextEdit()
		size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
		size_policy.setVerticalStretch(1)
		self.input_field.setSizePolicy(size_policy)
		self.input_field.setMaximumHeight(self.input_field.fontMetrics().lineSpacing())
		self.input_field.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
		self.input_field.textChanged.connect(self.adjust_input_field_size)
		self.input_field.textChanged.connect(self.update_send_button_text)
		self.input_field.setPlaceholderText("Type your message here...")
		self.input_layout.addWidget(self.input_field, alignment=Qt.AlignBottom)
		
		self.send_button = QPushButton('Send')
		self.send_button.clicked.connect(self.send_message)
		
		self.send_add_toggle = QCheckBox()
		self.send_add_toggle.setCheckState(Qt.Checked)
		self.send_add_toggle.stateChanged.connect(lambda: self.update_send_button_text())
		self.input_layout.addWidget(self.send_add_toggle, alignment=Qt.AlignBottom)
		
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
		message = None
		
		message_text = self.input_field.toPlainText()
		message = Message.from_role_content(self.role_combobox.currentText(), message_text)
			
		self.message_added.emit(
			self.conversation, 
			message,
			self.send_add_toggle.isChecked()
		)
		
		self.input_field.clear()
		
	def closeEvent(self, event):
		self.write_settings()
		super().closeEvent(event)
		
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Enter and event.modifiers() == Qt.ControlModifier:
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
	
	def render_message(self, message:Message):
		self.list_view.render_message(message)
	
	def update_send_button_text(self):
		#"Run" if has unrun command, change to run, and the input field is empty:
		if self.has_unrun_command and self.input_field.toPlainText() == "":
			if self.send_button.text() != "Run":
				self.send_button.setText("Run")
				try:
					self.send_button.clicked.disconnect(self.send_message)
				except TypeError:
					pass
				self.send_button.clicked.connect(self.confirm_command.emit)
		else:
			if self.send_button.text() == "Run":
				try:
					self.send_button.clicked.disconnect(self.confirm_command.emit)
				except TypeError:
					pass
				self.send_button.clicked.connect(self.send_message)
			self.send_button.setText("Send" if self.send_add_toggle.isChecked() else "Add")
	
	@property
	def has_unrun_command(self):
		return self._has_unrun_command
	
	@has_unrun_command.setter
	def has_unrun_command(self, value:bool):
		self._has_unrun_command = value
		self.update_send_button_text()