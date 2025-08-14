from PySide6.QtWidgets import QMainWindow, QMenu
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen
from src.setting import Settings

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self._dragging = False
        self.initUI()
        
    def initUI(self):
        self.setFixedSize(200, 200)
        # 用户也许可以修改窗口大小
        self.update_window_flags()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.set_initial_position()
        self._drag_position = QPoint()

    def set_initial_position(self):
        # 默认出现位置也可以修改，但是只设置四个角上的数据就行
        screen_geometry = self.screen().geometry()
        x = screen_geometry.width() - self.width() - 20
        y = screen_geometry.height() - self.height() - 20
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
        

        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(self.close)

        menu.exec_(event.globalPos())

    def toggle_always_on_top(self):
        current = self.settings.get_always_on_top()
        self.settings.set_always_on_top(not current)
        self.update_window_flags()
        self.show()

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

    def paintEvent(self, event):
        # 暂时先用在这里当替代吧
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(Qt.white)
        painter.drawEllipse(10, 10, 180, 180)
