import sys
import win32gui
import win32con
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.pet_window import DesktopPet

def hide_console_window():
    """隐藏控制台窗口（仅在打包成 .exe 运行时生效）"""
    try:
        # 检查程序是否在终端中运行
        # 如果 sys.stdout 和 sys.stderr 指向真实的终端，说明是在 CMD 中运行的
        # 如果是 None 或指向 NUL，说明是 GUI 模式运行
        if sys.stdout is None or sys.stderr is None:
            console = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(console, win32con.SW_HIDE)
    except:
        pass

def main():
    hide_console_window()
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    pet.destroyed.connect(app.quit)
    return_value = app.exec()
    sys.exit(return_value)

if __name__ == '__main__':
    main()
