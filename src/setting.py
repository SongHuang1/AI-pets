import os
from PySide6.QtCore import QSettings, QStandardPaths

class Settings:
    def __init__(self):
        data_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "DesktopPet")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        config_path = os.path.join(data_dir, "settings.ini")
        self.settings = QSettings(config_path, QSettings.IniFormat)
        if not os.path.exists(config_path):
            self.settings.setValue("always_on_top", False)
            self.settings.setValue("window_width", 200)
            self.settings.setValue("window_height", 200)

    def set_always_on_top(self, value):
        self.settings.setValue("always_on_top", value)

    def get_always_on_top(self):
        return self.settings.value("always_on_top", False, bool)

    def set_window_size(self, width, height):
        self.settings.setValue("window_width", width)
        self.settings.setValue("window_height", height)

    def get_window_size(self):
        width = self.settings.value("window_width", 200, int)
        height = self.settings.value("window_height", 200, int)
        return width, height

    def set_window_position(self, x, y):
        self.settings.setValue("window_x", x)
        self.settings.setValue("window_y", y)

    def get_window_position(self):
        x = self.settings.value("window_x", None)
        y = self.settings.value("window_y", None)
        return x, y
