from PySide6.QtGui import QPixmap, QPainter, QImage
from PySide6.QtCore import Qt
import os

class Resources:
    """宠物资源管理器"""
    
    def __init__(self):
        self._images = {}
        self._current_action = 'idle'
        self._action_frames = {}
        self._current_frame = 0
        self._load_default_images()
    
    def _load_default_images(self):
        """加载默认宠物图像"""
        # 创建默认的宠物图像（简单圆形）
        size = 100
        image = QImage(size, size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.white)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        
        self._images['idle'] = image
    
    def get_image(self, action='idle'):
        """获取指定动作的图像"""
        return self._images.get(action, self._images['idle'])
    
    def register_action(self, action_name, image_or_path):
        """注册新的动作图像"""
        if isinstance(image_or_path, str):
            if os.path.exists(image_or_path):
                image = QImage(image_or_path)
                self._images[action_name] = image
        else:
            self._images[action_name] = image_or_path
    
    def set_action(self, action):
        """设置当前动作"""
        if action in self._images:
            self._current_action = action
    
    def get_current_image(self):
        """获取当前图像"""
        return self.get_image(self._current_action)
