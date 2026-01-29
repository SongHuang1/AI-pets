"""
伴侣形象渲染系统
提供可扩展的伴侣形象基类和具体实现，支持动画效果
包含多种可爱风格：小猫、小狗、熊猫、简约风格和超可爱小兔子
"""

from abc import ABC, abstractmethod
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PySide6.QtCore import Qt, QTimer, QPointF
import math


class PetRendererBase(ABC):
    """
    伴侣形象渲染器基类
    所有伴侣形象都应该继承此类并实现 paint 方法
    """

    def __init__(self):
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._update_animation)
        self._blink_timer = QTimer()
        self._blink_timer.timeout.connect(self._update_blink)

        # 动画状态
        self._breathing_phase = 0.0  # 呼吸动画相位
        self._is_blinking = False  # 是否正在眨眼
        self._blink_progress = 0.0  # 眨眼进度 (0-1)
        self._blink_duration = 150  # 眨眼持续时间(毫秒)
        self._next_blink_time = 3000  # 下次眨眼时间(毫秒)

        # 启动动画
        self._animation_timer.start(50)  # 20fps
        self._schedule_next_blink()

    def _schedule_next_blink(self):
        """安排下次眨眼"""
        self._blink_timer.start(self._next_blink_time)

    def _update_animation(self):
        """更新呼吸动画"""
        self._breathing_phase = (self._breathing_phase + 0.05) % (2 * math.pi)

    def _update_blink(self):
        """更新眨眼状态"""
        if not self._is_blinking:
            self._is_blinking = True
            self._blink_progress = 0.0
            self._blink_timer.start(20)  # 更快更新眨眼进度
        else:
            self._blink_progress += 20 / self._blink_duration
            if self._blink_progress >= 1.0:
                self._is_blinking = False
                self._blink_progress = 0.0
                self._schedule_next_blink()

    def _get_breathing_scale(self):
        """获取呼吸缩放因子"""
        return 1.0 + 0.03 * math.sin(self._breathing_phase)

    def _get_eye_openness(self):
        """获取眼睛睁开程度 (0-1)"""
        if not self._is_blinking:
            return 1.0
        # 使用平滑的眨眼曲线
        return 1.0 - math.sin(self._blink_progress * math.pi)

    @abstractmethod
    def paint(self, painter: QPainter, width: int, height: int):
        """
        绘制伴侣形象

        Args:
            painter: QPainter 对象
            width: 绘制区域宽度
            height: 绘制区域高度
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """返回伴侣形象的名称"""
        pass


class CuteRabbitRenderer(PetRendererBase):
    """
    超可爱小兔子风格伴侣形象
    """

    def get_name(self) -> str:
        return "超可爱小兔"

    def paint(self, painter: QPainter, width: int, height: int):
        painter.setRenderHint(QPainter.Antialiasing)

        # 应用呼吸效果
        scale = self._get_breathing_scale()
        center_x = width / 2
        center_y = height / 2
        base_size = min(width, height) * 0.4

        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(scale, scale)
        painter.translate(-center_x, -center_y)

        # 绘制身体 (浅粉色椭圆)
        body_color = QColor(255, 230, 250)
        painter.setPen(QPen(QColor(240, 200, 230), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - base_size * 0.75), int(center_y - base_size * 0.15),
                          int(base_size * 1.5), int(base_size * 0.95))

        # 绘制肚子 (更浅的粉色)
        belly_color = QColor(255, 245, 252)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(belly_color))
        painter.drawEllipse(int(center_x - base_size * 0.42), int(center_y + base_size * 0.12),
                          int(base_size * 0.84), int(base_size * 0.55))

        # 绘制头部 (圆形)
        head_size = base_size * 0.9
        head_y = center_y - base_size * 0.45
        painter.setPen(QPen(QColor(240, 200, 230), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - head_size/2), int(head_y - head_size/2),
                          int(head_size), int(head_size * 0.95))

        # 绘制耳朵 (长耳朵)
        ear_color = QColor(255, 220, 240)
        inner_ear_color = QColor(255, 180, 220)
        painter.setBrush(QBrush(ear_color))
        # 左耳
        left_ear = QPainterPath()
        left_ear.moveTo(center_x - head_size * 0.3, head_y - head_size * 0.35)
        left_ear.lineTo(center_x - head_size * 0.45, head_y - head_size * 0.85)
        left_ear.lineTo(center_x - head_size * 0.15, head_y - head_size * 0.45)
        left_ear.closeSubpath()
        painter.drawPath(left_ear)
        # 右耳
        right_ear = QPainterPath()
        right_ear.moveTo(center_x + head_size * 0.3, head_y - head_size * 0.35)
        right_ear.lineTo(center_x + head_size * 0.45, head_y - head_size * 0.85)
        right_ear.lineTo(center_x + head_size * 0.15, head_y - head_size * 0.45)
        right_ear.closeSubpath()
        painter.drawPath(right_ear)
        
        # 绘制耳朵内侧
        painter.setBrush(QBrush(inner_ear_color))
        # 左耳内侧
        left_inner_ear = QPainterPath()
        left_inner_ear.moveTo(center_x - head_size * 0.28, head_y - head_size * 0.38)
        left_inner_ear.lineTo(center_x - head_size * 0.4, head_y - head_size * 0.8)
        left_inner_ear.lineTo(center_x - head_size * 0.18, head_y - head_size * 0.42)
        left_inner_ear.closeSubpath()
        painter.drawPath(left_inner_ear)
        # 右耳内侧
        right_inner_ear = QPainterPath()
        right_inner_ear.moveTo(center_x + head_size * 0.28, head_y - head_size * 0.38)
        right_inner_ear.lineTo(center_x + head_size * 0.4, head_y - head_size * 0.8)
        right_inner_ear.lineTo(center_x + head_size * 0.18, head_y - head_size * 0.42)
        right_inner_ear.closeSubpath()
        painter.drawPath(right_inner_ear)

        # 绘制眼睛 (大大的圆形眼睛)
        eye_openness = self._get_eye_openness()
        eye_size = head_size * 0.25  # 更大的眼睛
        eye_color = QColor(80, 60, 120)  # 紫色眼睛，更可爱
        painter.setPen(QPen(eye_color, 2))
        painter.setBrush(QBrush(eye_color))

        # 左眼
        left_eye_y = head_y + head_size * 0.02
        if eye_openness < 0.3:
            painter.drawLine(int(center_x - head_size * 0.25), int(left_eye_y),
                           int(center_x - head_size * 0.05), int(left_eye_y))
        else:
            painter.drawEllipse(int(center_x - head_size * 0.28), int(left_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x - head_size * 0.25), int(left_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.4), int(eye_size * 0.4 * eye_openness))

        # 右眼
        right_eye_y = head_y + head_size * 0.02
        painter.setBrush(QBrush(eye_color))
        if eye_openness < 0.3:
            painter.drawLine(int(center_x + head_size * 0.05), int(right_eye_y),
                           int(center_x + head_size * 0.25), int(right_eye_y))
        else:
            painter.drawEllipse(int(center_x + head_size * 0.05), int(right_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x + head_size * 0.08), int(right_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.4), int(eye_size * 0.4 * eye_openness))

        # 绘制鼻子 (粉色小三角)
        nose_size = head_size * 0.1
        nose_color = QColor(255, 170, 200)
        painter.setPen(QPen(QColor(240, 140, 170), 1))
        painter.setBrush(QBrush(nose_color))
        nose_path = QPainterPath()
        nose_x, nose_y = center_x, head_y + head_size * 0.25
        nose_path.moveTo(nose_x, nose_y - nose_size/2)
        nose_path.lineTo(nose_x - nose_size/2, nose_y + nose_size/2)
        nose_path.lineTo(nose_x + nose_size/2, nose_y + nose_size/2)
        nose_path.closeSubpath()
        painter.drawPath(nose_path)

        # 绘制嘴巴 (可爱的三瓣嘴)
        mouth_color = QColor(200, 120, 160)
        painter.setPen(QPen(mouth_color, 2))
        painter.setBrush(Qt.NoBrush)
        # 三瓣嘴的中央竖线
        painter.drawLine(int(center_x), int(head_y + head_size * 0.28),
                        int(center_x), int(head_y + head_size * 0.4))
        # 三瓣嘴的左右两瓣
        painter.drawLine(int(center_x - head_size * 0.1), int(head_y + head_size * 0.33),
                        int(center_x), int(head_y + head_size * 0.38))
        painter.drawLine(int(center_x + head_size * 0.1), int(head_y + head_size * 0.33),
                        int(center_x), int(head_y + head_size * 0.38))

        # 绘制腮红
        blush_color = QColor(255, 200, 230, 150)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(blush_color))
        painter.drawEllipse(int(center_x - head_size * 0.48), int(head_y + head_size * 0.08),
                          int(head_size * 0.25), int(head_size * 0.15))
        painter.drawEllipse(int(center_x + head_size * 0.23), int(head_y + head_size * 0.08),
                          int(head_size * 0.25), int(head_size * 0.15))

        # 绘制前爪
        paw_color = QColor(255, 220, 240)
        painter.setPen(QPen(QColor(240, 200, 230), 2))
        painter.setBrush(QBrush(paw_color))
        painter.drawEllipse(int(center_x - base_size * 0.48), int(center_y + base_size * 0.48),
                          int(base_size * 0.16), int(base_size * 0.13))
        painter.drawEllipse(int(center_x + base_size * 0.33), int(center_y + base_size * 0.48),
                          int(base_size * 0.16), int(base_size * 0.13))

        painter.restore()


class CuteCatRenderer(PetRendererBase):
    """
    可爱小猫风格伴侣形象
    """

    def get_name(self) -> str:
        return "可爱小猫"

    def paint(self, painter: QPainter, width: int, height: int):
        painter.setRenderHint(QPainter.Antialiasing)

        # 应用呼吸效果
        scale = self._get_breathing_scale()
        center_x = width / 2
        center_y = height / 2
        base_size = min(width, height) * 0.4

        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(scale, scale)
        painter.translate(-center_x, -center_y)

        # 绘制身体 (橙色椭圆)
        body_color = QColor(255, 200, 130)
        painter.setPen(QPen(QColor(210, 140, 80), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - base_size * 0.7), int(center_y - base_size * 0.2),
                          int(base_size * 1.4), int(base_size * 0.9))

        # 绘制肚子 (白色)
        belly_color = QColor(255, 255, 250)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(belly_color))
        painter.drawEllipse(int(center_x - base_size * 0.4), int(center_y + base_size * 0.1),
                          int(base_size * 0.8), int(base_size * 0.5))

        # 绘制头部 (圆形)
        head_size = base_size * 0.85
        head_y = center_y - base_size * 0.5
        painter.setPen(QPen(QColor(210, 140, 80), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - head_size/2), int(head_y - head_size/2),
                          int(head_size), int(head_size * 0.9))

        # 绘制耳朵
        ear_color = QColor(255, 180, 110)
        painter.setBrush(QBrush(ear_color))
        # 左耳
        left_ear = QPainterPath()
        left_ear.moveTo(center_x - head_size * 0.35, head_y - head_size * 0.35)
        left_ear.lineTo(center_x - head_size * 0.5, head_y - head_size * 0.85)
        left_ear.lineTo(center_x - head_size * 0.15, head_y - head_size * 0.45)
        left_ear.closeSubpath()
        painter.drawPath(left_ear)
        # 右耳
        right_ear = QPainterPath()
        right_ear.moveTo(center_x + head_size * 0.35, head_y - head_size * 0.35)
        right_ear.lineTo(center_x + head_size * 0.5, head_y - head_size * 0.85)
        right_ear.lineTo(center_x + head_size * 0.15, head_y - head_size * 0.45)
        right_ear.closeSubpath()
        painter.drawPath(right_ear)

        # 绘制眼睛
        eye_openness = self._get_eye_openness()
        eye_size = head_size * 0.22
        eye_color = QColor(50, 30, 20)
        painter.setPen(QPen(eye_color, 2))
        painter.setBrush(QBrush(eye_color))

        # 左眼
        left_eye_y = head_y + head_size * 0.03
        if eye_openness < 0.3:
            painter.drawLine(int(center_x - head_size * 0.28), int(left_eye_y),
                           int(center_x - head_size * 0.08), int(left_eye_y))
        else:
            painter.drawEllipse(int(center_x - head_size * 0.3), int(left_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x - head_size * 0.26), int(left_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.4), int(eye_size * 0.4 * eye_openness))

        # 右眼
        right_eye_y = head_y + head_size * 0.03
        painter.setBrush(QBrush(eye_color))
        if eye_openness < 0.3:
            painter.drawLine(int(center_x + head_size * 0.08), int(right_eye_y),
                           int(center_x + head_size * 0.28), int(right_eye_y))
        else:
            painter.drawEllipse(int(center_x + head_size * 0.08), int(right_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x + head_size * 0.12), int(right_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.4), int(eye_size * 0.4 * eye_openness))

        # 绘制鼻子
        nose_size = head_size * 0.12
        nose_color = QColor(255, 150, 150)
        painter.setPen(QPen(QColor(220, 110, 110), 1))
        painter.setBrush(QBrush(nose_color))
        painter.drawEllipse(int(center_x - nose_size/2), int(head_y + head_size * 0.2 - nose_size/2),
                          int(nose_size), int(nose_size))

        # 绘制嘴巴
        mouth_color = QColor(180, 110, 60)
        painter.setPen(QPen(mouth_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(int(center_x - nose_size/2), int(head_y + head_size * 0.27),
                        int(center_x - head_size * 0.18), int(head_y + head_size * 0.35))
        painter.drawLine(int(center_x + nose_size/2), int(head_y + head_size * 0.27),
                        int(center_x + head_size * 0.18), int(head_y + head_size * 0.35))

        # 绘制腮红
        blush_color = QColor(255, 170, 170, 150)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(blush_color))
        painter.drawEllipse(int(center_x - head_size * 0.48), int(head_y + head_size * 0.08),
                          int(head_size * 0.25), int(head_size * 0.14))
        painter.drawEllipse(int(center_x + head_size * 0.23), int(head_y + head_size * 0.08),
                          int(head_size * 0.25), int(head_size * 0.14))

        # 绘制前爪
        paw_color = QColor(255, 200, 130)
        painter.setPen(QPen(QColor(210, 140, 80), 2))
        painter.setBrush(QBrush(paw_color))
        painter.drawEllipse(int(center_x - base_size * 0.45), int(center_y + base_size * 0.45),
                          int(base_size * 0.15), int(base_size * 0.12))
        painter.drawEllipse(int(center_x + base_size * 0.3), int(center_y + base_size * 0.45),
                          int(base_size * 0.15), int(base_size * 0.12))

        painter.restore()


class CuteDogRenderer(PetRendererBase):
    """
    温馨小狗风格伴侣形象
    """

    def get_name(self) -> str:
        return "温馨小狗"

    def paint(self, painter: QPainter, width: int, height: int):
        painter.setRenderHint(QPainter.Antialiasing)

        # 应用呼吸效果
        scale = self._get_breathing_scale()
        center_x = width / 2
        center_y = height / 2
        base_size = min(width, height) * 0.4

        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(scale, scale)
        painter.translate(-center_x, -center_y)

        # 绘制身体 (棕色椭圆)
        body_color = QColor(230, 200, 160)
        painter.setPen(QPen(QColor(180, 150, 110), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - base_size * 0.7), int(center_y - base_size * 0.12),
                          int(base_size * 1.4), int(base_size * 0.85))

        # 绘制肚子 (白色)
        belly_color = QColor(250, 245, 235)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(belly_color))
        painter.drawEllipse(int(center_x - base_size * 0.38), int(center_y + base_size * 0.1),
                          int(base_size * 0.76), int(base_size * 0.5))

        # 绘制头部 (圆形)
        head_size = base_size * 0.92
        head_y = center_y - base_size * 0.42
        painter.setPen(QPen(QColor(180, 150, 110), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - head_size/2), int(head_y - head_size/2),
                          int(head_size), int(head_size * 0.93))

        # 绘制耳朵 (垂耳)
        ear_color = QColor(210, 180, 140)
        painter.setBrush(QBrush(ear_color))
        # 左耳
        left_ear = QPainterPath()
        left_ear.moveTo(center_x - head_size * 0.38, head_y - head_size * 0.22)
        left_ear.quadTo(center_x - head_size * 0.65, head_y - head_size * 0.12,
                        center_x - head_size * 0.58, head_y + head_size * 0.28)
        left_ear.quadTo(center_x - head_size * 0.42, head_y + head_size * 0.32,
                        center_x - head_size * 0.32, head_y - head_size * 0.08)
        left_ear.quadTo(center_x - head_size * 0.35, head_y - head_size * 0.18,
                        center_x - head_size * 0.38, head_y - head_size * 0.22)
        painter.drawPath(left_ear)
        # 右耳
        right_ear = QPainterPath()
        right_ear.moveTo(center_x + head_size * 0.38, head_y - head_size * 0.22)
        right_ear.quadTo(center_x + head_size * 0.65, head_y - head_size * 0.12,
                         center_x + head_size * 0.58, head_y + head_size * 0.28)
        right_ear.quadTo(center_x + head_size * 0.42, head_y + head_size * 0.32,
                         center_x + head_size * 0.32, head_y - head_size * 0.08)
        right_ear.quadTo(center_x + head_size * 0.35, head_y - head_size * 0.18,
                         center_x + head_size * 0.38, head_y - head_size * 0.22)
        painter.drawPath(right_ear)

        # 绘制眼睛
        eye_openness = self._get_eye_openness()
        eye_size = head_size * 0.2
        eye_color = QColor(75, 55, 45)
        painter.setPen(QPen(eye_color, 2))
        painter.setBrush(QBrush(eye_color))

        # 左眼
        left_eye_y = head_y + head_size * 0.04
        if eye_openness < 0.3:
            painter.drawLine(int(center_x - head_size * 0.26), int(left_eye_y),
                           int(center_x - head_size * 0.08), int(left_eye_y))
        else:
            painter.drawEllipse(int(center_x - head_size * 0.28), int(left_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x - head_size * 0.24), int(left_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.42), int(eye_size * 0.42 * eye_openness))

        # 右眼
        right_eye_y = head_y + head_size * 0.04
        painter.setBrush(QBrush(eye_color))
        if eye_openness < 0.3:
                    painter.drawLine(int(center_x + head_size * 0.08), int(right_eye_y),
                                   int(center_x + head_size * 0.26), int(right_eye_y))
        else:
            painter.drawEllipse(int(center_x + head_size * 0.08), int(right_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x + head_size * 0.12), int(right_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.42), int(eye_size * 0.42 * eye_openness))

        # 绘制鼻子
        nose_size = head_size * 0.13
        nose_color = QColor(50, 35, 25)
        painter.setPen(QPen(nose_color, 1))
        painter.setBrush(QBrush(nose_color))
        painter.drawEllipse(int(center_x - nose_size/2), int(head_y + head_size * 0.22 - nose_size/2),
                          int(nose_size), int(nose_size))

        # 绘制嘴巴
        mouth_color = QColor(160, 120, 80)
        painter.setPen(QPen(mouth_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(int(center_x - nose_size/2), int(head_y + head_size * 0.3),
                        int(center_x - head_size * 0.18), int(head_y + head_size * 0.38))
        painter.drawLine(int(center_x + nose_size/2), int(head_y + head_size * 0.3),
                        int(center_x + head_size * 0.18), int(head_y + head_size * 0.38))
        painter.drawLine(int(center_x - head_size * 0.18), int(head_y + head_size * 0.38),
                        int(center_x), int(head_y + head_size * 0.43))
        painter.drawLine(int(center_x), int(head_y + head_size * 0.43),
                        int(center_x + head_size * 0.18), int(head_y + head_size * 0.38))

        # 绘制舌头
        tongue_color = QColor(255, 170, 170)
        painter.setPen(QPen(QColor(240, 140, 140), 1))
        painter.setBrush(QBrush(tongue_color))
        tongue_path = QPainterPath()
        tongue_path.moveTo(center_x - head_size * 0.1, head_y + head_size * 0.43)
        tongue_path.quadTo(center_x, head_y + head_size * 0.68,
                         center_x + head_size * 0.1, head_y + head_size * 0.43)
        painter.drawPath(tongue_path)

        # 绘制前爪
        paw_color = QColor(230, 200, 160)
        painter.setPen(QPen(QColor(180, 150, 110), 2))
        painter.setBrush(QBrush(paw_color))
        painter.drawEllipse(int(center_x - base_size * 0.45), int(center_y + base_size * 0.45),
                          int(base_size * 0.15), int(base_size * 0.12))
        painter.drawEllipse(int(center_x + base_size * 0.3), int(center_y + base_size * 0.45),
                          int(base_size * 0.15), int(base_size * 0.12))

        painter.restore()


class MinimalistRenderer(PetRendererBase):
    """
    简约抽象风格伴侣形象
    """

    def get_name(self) -> str:
        return "简约伙伴"

    def paint(self, painter: QPainter, width: int, height: int):
        painter.setRenderHint(QPainter.Antialiasing)

        # 应用呼吸效果
        scale = self._get_breathing_scale()
        center_x = width / 2
        center_y = height / 2
        base_size = min(width, height) * 0.4

        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(scale, scale)
        painter.translate(-center_x, -center_y)

        # 绘制身体 (粉色椭圆)
        body_color = QColor(255, 240, 245)
        painter.setPen(QPen(QColor(250, 210, 225), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - base_size * 0.7), int(center_y - base_size * 0.25),
                          int(base_size * 1.4), int(base_size * 1.0))

        # 绘制肚子 (浅色)
        belly_color = QColor(255, 252, 253)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(belly_color))
        painter.drawEllipse(int(center_x - base_size * 0.4), int(center_y + base_size * 0.08),
                          int(base_size * 0.8), int(base_size * 0.52))

        # 绘制头部 (圆形)
        head_size = base_size * 0.95
        head_y = center_y - base_size * 0.4
        painter.setPen(QPen(QColor(250, 210, 225), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - head_size/2), int(head_y - head_size/2),
                          int(head_size), int(head_size))

        # 绘制耳朵
        ear_color = QColor(255, 235, 245)
        painter.setBrush(QBrush(ear_color))
        # 左耳
        left_ear = QPainterPath()
        left_ear.moveTo(center_x - head_size * 0.32, head_y - head_size * 0.35)
        left_ear.quadTo(center_x - head_size * 0.42, head_y - head_size * 0.7,
                        center_x - head_size * 0.18, head_y - head_size * 0.45)
        left_ear.quadTo(center_x - head_size * 0.28, head_y - head_size * 0.35,
                        center_x - head_size * 0.32, head_y - head_size * 0.35)
        painter.drawPath(left_ear)
        # 右耳
        right_ear = QPainterPath()
        right_ear.moveTo(center_x + head_size * 0.32, head_y - head_size * 0.35)
        right_ear.quadTo(center_x + head_size * 0.42, head_y - head_size * 0.7,
                         center_x + head_size * 0.18, head_y - head_size * 0.45)
        right_ear.quadTo(center_x + head_size * 0.28, head_y - head_size * 0.35,
                         center_x + head_size * 0.32, head_y - head_size * 0.35)
        painter.drawPath(right_ear)

        # 绘制眼睛
        eye_openness = self._get_eye_openness()
        eye_size = head_size * 0.18
        eye_color = QColor(100, 80, 100)
        painter.setPen(QPen(eye_color, 2))
        painter.setBrush(QBrush(eye_color))

        # 左眼
        left_eye_y = head_y + head_size * 0.06
        if eye_openness < 0.3:
            painter.drawLine(int(center_x - head_size * 0.24), int(left_eye_y),
                           int(center_x - head_size * 0.08), int(left_eye_y))
        else:
            painter.drawEllipse(int(center_x - head_size * 0.26), int(left_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x - head_size * 0.23), int(left_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.45), int(eye_size * 0.45 * eye_openness))

        # 右眼
        right_eye_y = head_y + head_size * 0.06
        painter.setBrush(QBrush(eye_color))
        if eye_openness < 0.3:
            painter.drawLine(int(center_x + head_size * 0.08), int(right_eye_y),
                           int(center_x + head_size * 0.24), int(right_eye_y))
        else:
            painter.drawEllipse(int(center_x + head_size * 0.08), int(right_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x + head_size * 0.11), int(right_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.45), int(eye_size * 0.45 * eye_openness))

        # 绘制嘴巴
        mouth_color = QColor(170, 120, 150)
        painter.setPen(QPen(mouth_color, 2.5))
        painter.setBrush(Qt.NoBrush)
        mouth_path = QPainterPath()
        mouth_path.moveTo(center_x - head_size * 0.16, head_y + head_size * 0.28)
        mouth_path.quadTo(center_x, head_y + head_size * 0.42,
                         center_x + head_size * 0.16, head_y + head_size * 0.28)
        painter.drawPath(mouth_path)

        # 绘制腮红
        blush_color = QColor(255, 200, 220, 150)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(blush_color))
        painter.drawEllipse(int(center_x - head_size * 0.48), int(head_y + head_size * 0.12),
                          int(head_size * 0.22), int(head_size * 0.13))
        painter.drawEllipse(int(center_x + head_size * 0.26), int(head_y + head_size * 0.12),
                          int(head_size * 0.22), int(head_size * 0.13))

        painter.restore()


class CutePandaRenderer(PetRendererBase):
    """
    可爱熊猫风格伴侣形象
    """

    def get_name(self) -> str:
        return "可爱熊猫"

    def paint(self, painter: QPainter, width: int, height: int):
        painter.setRenderHint(QPainter.Antialiasing)

        # 应用呼吸效果
        scale = self._get_breathing_scale()
        center_x = width / 2
        center_y = height / 2
        base_size = min(width, height) * 0.4

        painter.save()
        painter.translate(center_x, center_y)
        painter.scale(scale, scale)
        painter.translate(-center_x, -center_y)

        # 绘制身体 (白色椭圆)
        body_color = QColor(250, 250, 250)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - base_size * 0.65), int(center_y - base_size * 0.12),
                          int(base_size * 1.3), int(base_size * 0.85))

        # 绘制肚子 (纯白色)
        belly_color = QColor(255, 255, 255)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(belly_color))
        painter.drawEllipse(int(center_x - base_size * 0.38), int(center_y + base_size * 0.1),
                          int(base_size * 0.76), int(base_size * 0.5))

        # 绘制头部 (白色大圆形)
        head_size = base_size * 0.95
        head_y = center_y - base_size * 0.42
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(body_color))
        painter.drawEllipse(int(center_x - head_size/2), int(head_y - head_size/2),
                          int(head_size), int(head_size * 0.95))

        # 绘制耳朵 (黑色圆耳)
        ear_color = QColor(60, 60, 60)
        painter.setBrush(QBrush(ear_color))
        # 左耳
        left_ear = QPainterPath()
        left_ear.moveTo(center_x - head_size * 0.32, head_y - head_size * 0.35)
        left_ear.quadTo(center_x - head_size * 0.5, head_y - head_size * 0.75,
                        center_x - head_size * 0.15, head_y - head_size * 0.45)
        left_ear.quadTo(center_x - head_size * 0.25, head_y - head_size * 0.35,
                        center_x - head_size * 0.32, head_y - head_size * 0.35)
        painter.drawPath(left_ear)
        # 右耳
        right_ear = QPainterPath()
        right_ear.moveTo(center_x + head_size * 0.32, head_y - head_size * 0.35)
        right_ear.quadTo(center_x + head_size * 0.5, head_y - head_size * 0.75,
                         center_x + head_size * 0.15, head_y - head_size * 0.45)
        right_ear.quadTo(center_x + head_size * 0.25, head_y - head_size * 0.35,
                         center_x + head_size * 0.32, head_y - head_size * 0.35)
        painter.drawPath(right_ear)

        # 绘制眼圈 (黑色眼圈)
        eye_patch_color = QColor(60, 60, 60)
        painter.setBrush(QBrush(eye_patch_color))
        painter.setPen(Qt.NoPen)
        # 左眼圈
        left_patch = QPainterPath()
        left_patch.moveTo(center_x - head_size * 0.38, head_y + head_size * 0.0)
        left_patch.quadTo(center_x - head_size * 0.55, head_y + head_size * 0.05,
                          center_x - head_size * 0.52, head_y + head_size * 0.25)
        left_patch.quadTo(center_x - head_size * 0.32, head_y + head_size * 0.28,
                          center_x - head_size * 0.2, head_y + head_size * 0.1)
        left_patch.quadTo(center_x - head_size * 0.25, head_y - head_size * 0.05,
                          center_x - head_size * 0.38, head_y + head_size * 0.0)
        painter.drawPath(left_patch)
        # 右眼圈
        right_patch = QPainterPath()
        right_patch.moveTo(center_x + head_size * 0.38, head_y + head_size * 0.0)
        right_patch.quadTo(center_x + head_size * 0.55, head_y + head_size * 0.05,
                           center_x + head_size * 0.52, head_y + head_size * 0.25)
        right_patch.quadTo(center_x + head_size * 0.32, head_y + head_size * 0.28,
                           center_x + head_size * 0.2, head_y + head_size * 0.1)
        right_patch.quadTo(center_x + head_size * 0.25, head_y - head_size * 0.05,
                           center_x + head_size * 0.38, head_y + head_size * 0.0)
        painter.drawPath(right_patch)

        # 绘制眼睛
        eye_openness = self._get_eye_openness()
        eye_size = head_size * 0.2
        eye_color = QColor(30, 30, 30)
        painter.setPen(QPen(eye_color, 2))
        painter.setBrush(QBrush(eye_color))

        # 左眼
        left_eye_y = head_y + head_size * 0.08
        if eye_openness < 0.3:
            painter.drawLine(int(center_x - head_size * 0.35), int(left_eye_y),
                           int(center_x - head_size * 0.15), int(left_eye_y))
        else:
            painter.drawEllipse(int(center_x - head_size * 0.38), int(left_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x - head_size * 0.34), int(left_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.5), int(eye_size * 0.5 * eye_openness))

        # 右眼
        right_eye_y = head_y + head_size * 0.08
        painter.setBrush(QBrush(eye_color))
        if eye_openness < 0.3:
            painter.drawLine(int(center_x + head_size * 0.15), int(right_eye_y),
                           int(center_x + head_size * 0.35), int(right_eye_y))
        else:
            painter.drawEllipse(int(center_x + head_size * 0.15), int(right_eye_y - eye_size/2),
                              int(eye_size), int(eye_size * eye_openness))
            # 高光
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(int(center_x + head_size * 0.19), int(right_eye_y - eye_size/2 + 2),
                              int(eye_size * 0.5), int(eye_size * 0.5 * eye_openness))

        # 绘制鼻子
        nose_size = head_size * 0.1
        nose_color = QColor(60, 60, 60)
        painter.setPen(QPen(nose_color, 1))
        painter.setBrush(QBrush(nose_color))
        painter.drawEllipse(int(center_x - nose_size/2), int(head_y + head_size * 0.28 - nose_size/2),
                          int(nose_size), int(nose_size))

        # 绘制嘴巴
        mouth_color = QColor(180, 180, 180)
        painter.setPen(QPen(mouth_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(int(center_x - nose_size/2), int(head_y + head_size * 0.36),
                        int(center_x - head_size * 0.18), int(head_y + head_size * 0.44))
        painter.drawLine(int(center_x + nose_size/2), int(head_y + head_size * 0.36),
                        int(center_x + head_size * 0.18), int(head_y + head_size * 0.44))

        # 绘制腮红
        blush_color = QColor(255, 220, 225, 120)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(blush_color))
        painter.drawEllipse(int(center_x - head_size * 0.48), int(head_y + head_size * 0.18),
                          int(head_size * 0.2), int(head_size * 0.11))
        painter.drawEllipse(int(center_x + head_size * 0.28), int(head_y + head_size * 0.18),
                          int(head_size * 0.2), int(head_size * 0.11))

        # 绘制前爪
        paw_color = QColor(250, 250, 250)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(paw_color))
        painter.drawEllipse(int(center_x - base_size * 0.45), int(center_y + base_size * 0.45),
                          int(base_size * 0.15), int(base_size * 0.12))
        painter.drawEllipse(int(center_x + base_size * 0.3), int(center_y + base_size * 0.45),
                          int(base_size * 0.15), int(base_size * 0.12))

        painter.restore()


class PetRendererFactory:
    """
    伴侣形象渲染器工厂类
    用于创建和管理所有的伴侣形象渲染器
    """

    _renderers = {
        "cute_cat": CuteCatRenderer,
        "cute_dog": CuteDogRenderer,
        "minimalist": MinimalistRenderer,
        "cute_panda": CutePandaRenderer,
        "cute_rabbit": CuteRabbitRenderer,
    }

    @classmethod
    def create_renderer(cls, renderer_type: str) -> PetRendererBase:
        """
        创建指定类型的伴侣形象渲染器

        Args:
            renderer_type: 渲染器类型标识符

        Returns:
            PetRendererBase 实例

        Raises:
            ValueError: 如果指定的类型不存在
        """
        if renderer_type not in cls._renderers:
            raise ValueError(f"未知的伴侣形象类型: {renderer_type}")
        return cls._renderers[renderer_type]()

    @classmethod
    def get_all_renderers(cls):
        """获取所有可用的渲染器类型"""
        return list(cls._renderers.keys())

    @classmethod
    def get_renderer_names(cls):
        """获取所有渲染器的显示名称"""
        return {key: renderer_class().get_name()
                for key, renderer_class in cls._renderers.items()}

    @classmethod
    def register_renderer(cls, key: str, renderer_class):
        """
        注册新的伴侣形象渲染器
        用于扩展新的伴侣形象

        Args:
            key: 渲染器类型标识符
            renderer_class: 渲染器类（必须继承自 PetRendererBase）
        """
        if not issubclass(renderer_class, PetRendererBase):
            raise TypeError("渲染器类必须继承自 PetRendererBase")
        cls._renderers[key] = renderer_class