from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTextEdit, QScrollArea, QWidget)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from src.ai_service import AIService


class AIChatWorker(QThread):
    """AI 对话工作线程"""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, ai_service: AIService, messages: list):
        super().__init__()
        self.ai_service = ai_service
        self.messages = messages

    def run(self):
        try:
            response = self.ai_service.chat(self.messages)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class AIChatDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.messages = []
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI 对话")
        self.setFixedSize(450, 500)

        layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        layout.addWidget(self.scroll_area, 1)

        input_layout = QHBoxLayout()
        self.input_edit = QTextEdit()
        self.input_edit.setMaximumHeight(60)
        self.input_edit.setPlaceholderText("输入您的问题...")
        self.input_edit.installEventFilter(self)

        send_button = QPushButton("发送")
        send_button.clicked.connect(self.send_message)

        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_history)

        input_layout.addWidget(self.input_edit, 1)
        input_layout.addWidget(send_button)
        input_layout.addWidget(clear_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

        if not self.settings.get_api_key():
            self.add_message("系统", "请先在设置中配置 API Key")

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj == self.input_edit:
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key_Return:
                if event.modifiers() == Qt.ControlModifier:
                    return False
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def add_message(self, role: str, content: str):
        message_label = QLabel(content)
        message_label.setWordWrap(True)
        message_label.setTextFormat(Qt.PlainText)
        message_label.setMaximumWidth(350)

        font = QFont()
        font.setPointSize(10)
        message_label.setFont(font)

        container = QWidget()
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(10, 5, 10, 5)

        if role == "user":
            message_label.setStyleSheet("""
                background-color: #90EE90;
                border-radius: 10px;
                padding: 8px;
            """)
            container_layout.addStretch()
            container_layout.addWidget(message_label)
        elif role == "assistant":
            message_label.setStyleSheet("""
                background-color: #D3D3D3;
                border-radius: 10px;
                padding: 8px;
            """)
            container_layout.addWidget(message_label)
            container_layout.addStretch()
        else:
            message_label.setStyleSheet("""
                background-color: #87CEEB;
                border-radius: 10px;
                padding: 8px;
                font-style: italic;
            """)
            container_layout.addStretch()
            container_layout.addWidget(message_label)

        container.setLayout(container_layout)
        self.scroll_layout.addWidget(container)

        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def send_message(self):
        user_input = self.input_edit.toPlainText().strip()
        if not user_input:
            return

        api_key = self.settings.get_api_key()
        if not api_key:
            self.add_message("系统", "请先在设置中配置 API Key")
            return

        if self.worker and self.worker.isRunning():
            return

        self.add_message("用户", user_input)
        self.input_edit.clear()

        self.messages.append({"role": "user", "content": user_input})

        loading_label = QLabel("AI 正在思考...")
        loading_label.setStyleSheet("font-style: italic; color: #666;")
        loading_container = QWidget()
        loading_layout = QHBoxLayout()
        loading_layout.setContentsMargins(10, 5, 10, 5)
        loading_layout.addWidget(loading_label)
        loading_layout.addStretch()
        loading_container.setLayout(loading_layout)
        self.scroll_layout.addWidget(loading_container)
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

        ai_service = AIService(
            api_key=api_key,
            base_url=self.settings.get_api_base_url(),
            model=self.settings.get_api_model()
        )

        self.worker = AIChatWorker(ai_service, self.messages.copy())
        self.worker.finished.connect(lambda response: self.on_response(response, loading_container))
        self.worker.error.connect(lambda error: self.on_error(error, loading_container))
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def on_response(self, response: str, loading_container: QWidget):
        loading_container.setParent(None)
        self.add_message("AI", response)
        self.messages.append({"role": "assistant", "content": response})
        self.worker = None

    def on_error(self, error: str, loading_container: QWidget):
        loading_container.setParent(None)
        self.add_message("系统", f"发生错误: {error}")
        self.worker = None

    def clear_history(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.messages.clear()
