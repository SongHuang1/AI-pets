
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
                              QPushButton, QComboBox, QApplication, QMessageBox, QLineEdit, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, QPoint

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("设置")
        self.setFixedSize(400, 380)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        # ===================设置窗口大小和位置========================
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("窗口宽度:"))

        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 500)
        current_width, current_height = self.settings.get_window_size()
        self.width_spin.setValue(current_width)

        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("窗口高度:"))

        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 500)
        self.height_spin.setValue(current_height)

        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout)

        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("窗口位置:"))

        self.position_combo = QComboBox()
        self.position_combo.addItems(["左上角", "右上角", "左下角", "右下角"])
        
        current_x, current_y = self.settings.get_window_position()
        if current_x is not None and current_y is not None:
            try:
                current_x = int(current_x)
                current_y = int(current_y)
                screen_geometry = QApplication.primaryScreen().geometry()
                # 给窗口大小修改留下可能的空隙
                window_width = self.settings.get_window_size()[0]
                window_height = self.settings.get_window_size()[1]
                
                if current_x <= 20 and current_y <= 20:
                    self.position_combo.setCurrentIndex(0) # 左上角
                elif current_x >= screen_geometry.width() - window_width - 20 and current_y <= 20:
                    self.position_combo.setCurrentIndex(1) # 右上角
                elif current_x <= 20 and current_y >= screen_geometry.height() - window_height - 20:
                    self.position_combo.setCurrentIndex(2)  # 左下角
                else:
                    self.position_combo.setCurrentIndex(3)  # 右下角
            except (ValueError, TypeError):
                self.position_combo.setCurrentIndex(3)
        
        position_layout.addWidget(self.position_combo)
        layout.addLayout(position_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        
        # =============数据删除================
        delete_button = QPushButton("删除所有数据")
        delete_button.setObjectName("delete_button")
        delete_button.clicked.connect(self.confirm_delete_data)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        # ===================AI 设置分组========================
        ai_group = QGroupBox("AI 设置")
        ai_layout = QFormLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("输入 API Key")
        self.api_key_input.setText(self.settings.get_api_key())

        self.api_base_url_input = QLineEdit()
        self.api_base_url_input.setPlaceholderText("https://api.openai.com/v1")
        self.api_base_url_input.setText(self.settings.get_api_base_url())

        self.api_model_input = QLineEdit()
        self.api_model_input.setPlaceholderText("gpt-3.5-turbo")
        self.api_model_input.setText(self.settings.get_api_model())

        ai_layout.addRow("API Key:", self.api_key_input)
        ai_layout.addRow("Base URL:", self.api_base_url_input)
        ai_layout.addRow("Model:", self.api_model_input)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        self.setLayout(layout)

    def save_settings(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        self.settings.set_window_size(width, height)

        position_text = self.position_combo.currentText()
        screen_geometry = QApplication.primaryScreen().geometry()

        if position_text == "左上角":
            x = 20
            y = 20
        elif position_text == "右上角":
            x = screen_geometry.width() - width - 20
            y = 20
        elif position_text == "左下角":
            x = 20
            y = screen_geometry.height() - height - 60
        else:  # 右下角
            x = screen_geometry.width() - width - 20
            y = screen_geometry.height() - height - 60

        self.settings.set_window_position(x, y)

        # 保存 AI 设置
        api_key = self.api_key_input.text().strip()
        api_base_url = self.api_base_url_input.text().strip()
        api_model = self.api_model_input.text().strip()

        if api_key:
            self.settings.set_api_key(api_key)
        if api_base_url:
            self.settings.set_api_base_url(api_base_url)
        if api_model:
            self.settings.set_api_model(api_model)

        if self.parent():
            self.parent().move(x, y)
        self.accept()
    
    def confirm_delete_data(self):
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除所有使用数据吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_data()
    
    def delete_data(self):
        self.settings.delete_all_data()
        QMessageBox.information(
            self, 
            "删除成功", 
            "所有数据已成功删除。程序即将退出。"
        )
        self.accept()
        if self.parent():
            self.parent().close()
