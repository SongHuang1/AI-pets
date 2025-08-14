from PySide6.QtCore import QSettings

class Settings:
    def __init__(self):
        self.settings = QSettings("DesktopPet", "PetApp")
    
    def set_always_on_top(self, value):
        self.settings.setValue("always_on_top", value)

    def get_always_on_top(self):
        return self.settings.value("always_on_top", False, bool)
