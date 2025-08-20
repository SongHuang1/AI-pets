from PySide6.QtWidgets import QMainWindow, QMenu, QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen
from src.setting import Settings
from src.settings_dialog import SettingsDialog
from src.usage_stats_dialog import UsageStatsDialog
from src.usage_tracker import UsageTracker

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self._dragging = False
        self.usage_tracker = UsageTracker()
        self.initUI()

    def initUI(self):
        width, height = self.settings.get_window_size()
        self.setFixedSize(width, height)
        self.update_window_flags()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.set_initial_position()
        self._drag_position = QPoint()

    def set_initial_position(self):
        x, y = self.settings.get_window_position()
        if x is None or y is None:
            screen_geometry = self.screen().geometry()
            x = screen_geometry.width() - self.width() - 20
            y = screen_geometry.height() - self.height() - 20
        else:
            x = int(x)
            y = int(y)
        self.move(x, y)

    def update_window_flags(self):
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.settings.get_always_on_top():
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        always_on_top_action = menu.addAction("始终置顶")
        always_on_top_action.setCheckable(True)
        always_on_top_action.setChecked(self.settings.get_always_on_top())
        always_on_top_action.triggered.connect(self.toggle_always_on_top)

        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(self.open_settings_dialog)
        
        stats_action = menu.addAction("使用统计")
        stats_action.triggered.connect(self.show_usage_stats)

        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(self.close)

        menu.exec_(event.globalPos())

    def toggle_always_on_top(self):
        current = self.settings.get_always_on_top()
        self.settings.set_always_on_top(not current)
        self.update_window_flags()
        self.show()

    def open_settings_dialog(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec_():
            width, height = self.settings.get_window_size()
            self.setFixedSize(width, height)
            self.set_initial_position()
            self.update_window_flags()
    
    def show_usage_stats(self):
        stats_dialog = UsageStatsDialog(self)
        stats_dialog.exec_()

    def mousePressEvent(self, event):
        # 单击还有动画播放，这里是不是没设计好
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

    def closeEvent(self, event):
        event.accept()
        QApplication.quit()

    def paintEvent(self, event):
        # 暂时先用在这里当替代吧
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(Qt.white)
        painter.drawEllipse(10, 10, 180, 180)
