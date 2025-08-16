
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QComboBox, QApplication
from PySide6.QtCore import Qt, QPoint

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("设置")
        self.setFixedSize(300, 200)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

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
                window_width = self.settings.get_window_size()[0]
                window_height = self.settings.get_window_size()[1]
                
                if current_x <= 20 and current_y <= 20:
                    self.position_combo.setCurrentIndex(0)
                elif current_x >= screen_geometry.width() - window_width - 20 and current_y <= 20:
                    self.position_combo.setCurrentIndex(1)
                elif current_x <= 20 and current_y >= screen_geometry.height() - window_height - 20:
                    self.position_combo.setCurrentIndex(2)
                else:
                    self.position_combo.setCurrentIndex(3)
            except (ValueError, TypeError):
                self.position_combo.setCurrentIndex(3)
        
        position_layout.addWidget(self.position_combo)
        layout.addLayout(position_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

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
        if self.parent():
            self.parent().move(x, y)
        self.accept()
