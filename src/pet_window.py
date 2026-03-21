from PySide6.QtWidgets import QMainWindow, QMenu, QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QImage
from src.setting import Settings
from src.settings_dialog import SettingsDialog
from src.usage_stats_dialog import UsageStatsDialog
from src.usage_tracker import UsageTracker
from src.ai_chat_dialog import AIChatDialog
from src.rescourse import Resources


class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self._dragging = False
        self.usage_tracker = UsageTracker()
        self.resources = Resources()
        self.initUI()

    def initUI(self):
        width, height = self.settings.get_window_size()
        self.setFixedSize(width, height)
        self.update_window_flags()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.set_position()
        self._drag_position = QPoint()

    def set_position(self):
        x, y = self.settings.get_window_position()
        if x is None or y is None:
            screen_geometry = self.screen().geometry()
            x = screen_geometry.width() - self.width() - 20
            y = screen_geometry.height() - self.height() - 20
        else:
            try:
                x, y = int(x), int(y)
            except:
                raise TypeError("不合法的输入")
        self.move(x, y)

    def update_window_flags(self):
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.settings.get_always_on_top():
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def toggle_always_on_top(self):
        current = self.settings.get_always_on_top()
        self.settings.set_always_on_top(not current)
        self.update_window_flags()
        self.show()
    
    def closeEvent(self, event):
        event.accept()
        QApplication.quit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        always_on_top_action = menu.addAction("始终置顶")
        always_on_top_action.setCheckable(True)
        always_on_top_action.setChecked(self.settings.get_always_on_top())
        always_on_top_action.triggered.connect(self.toggle_always_on_top)

        ai_chat_action = menu.addAction("AI 对话")
        ai_chat_action.triggered.connect(self.open_ai_chat)

        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(self.open_settings_dialog)
        
        stats_action = menu.addAction("使用统计")
        stats_action.triggered.connect(self.show_usage_stats)

        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(self.close)

        menu.exec_(event.globalPos())



    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_():
            width, height = self.settings.get_window_size()
            self.setFixedSize(width, height)
            self.set_position()
            self.update_window_flags()
    
    def show_usage_stats(self):
        stats_dialog = UsageStatsDialog(self.usage_tracker, self)
        stats_dialog.exec_()

    def open_ai_chat(self):
        ai_chat_dialog = AIChatDialog(self.settings, self)
        ai_chat_dialog.exec_()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取当前宠物图像
        image = self.resources.get_current_image()
        
        # 缩放图像以适应窗口大小
        scaled_image = image.scaled(self.width(), self.height(), 
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # 计算居中位置
        x = (self.width() - scaled_image.width()) // 2
        y = (self.height() - scaled_image.height()) // 2
        
        painter.drawImage(x, y, scaled_image)
