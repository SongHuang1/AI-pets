import os
import shutil
from typing import Optional, Tuple
from PySide6.QtCore import QSettings, QStandardPaths

class Settings:
    def __init__(self) -> None:
        data_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "DesktopPet")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        config_path = os.path.join(data_dir, "settings.ini")
        self.settings = QSettings(config_path, QSettings.IniFormat)
        if not os.path.exists(config_path):
            self.settings.setValue("always_on_top", False)
            self.settings.setValue("window_width", 200)
            self.settings.setValue("window_height", 200)

    def set_always_on_top(self, value: bool) -> None:
        self.settings.setValue("always_on_top", value)

    def get_always_on_top(self) -> bool:
        return self.settings.value("always_on_top", False, bool)

    def set_window_size(self, width: int, height: int) -> None:
        self.settings.setValue("window_width", width)
        self.settings.setValue("window_height", height)

    def get_window_size(self) -> Tuple[int, int]:
        width = self.settings.value("window_width", 200, int)
        height = self.settings.value("window_height", 200, int)
        return width, height

    def set_window_position(self, x: int, y: int) -> None:
        self.settings.setValue("window_x", x)
        self.settings.setValue("window_y", y)

    def get_window_position(self) -> Tuple[Optional[str], Optional[str]]:
        x = self.settings.value("window_x", None)
        y = self.settings.value("window_y", None)
        return x, y
    
    def delete_all_data(self) -> None:
        data_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "DesktopPet")
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)

        config_path = os.path.join(data_dir, "settings.ini")
        self.settings = QSettings(config_path, QSettings.IniFormat)
        self.settings.setValue("always_on_top", False)
        self.settings.setValue("window_width", 200)
        self.settings.setValue("window_height", 200)

    def set_api_key(self, api_key: str) -> None:
        self.settings.setValue("api_key", api_key)

    def get_api_key(self) -> str:
        return self.settings.value("api_key", "", str)

    def set_api_base_url(self, base_url: str) -> None:
        self.settings.setValue("api_base_url", base_url)

    def get_api_base_url(self) -> str:
        return self.settings.value("api_base_url", "https://api.openai.com/v1", str)

    def set_api_model(self, model: str) -> None:
        self.settings.setValue("api_model", model)

    def get_api_model(self) -> str:
        return self.settings.value("api_model", "gpt-3.5-turbo", str)
