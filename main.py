import sys
import win32gui
import win32con
import win32api
import winerror
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from src.pet_window import DesktopPet

MUTEX_NAME = "DesktopPet_SingleInstance_Mutex"

def check_single_instance():
    """检测程序是否已有实例在运行"""
    try:
        mutex = win32api.CreateMutex(None, False, MUTEX_NAME)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            return False
        return True
    except (win32api.error, WindowsError) as e:
        print(f"单实例检测失败: {e}")
        return True

def hide_console_window():
    """隐藏控制台窗口（仅在打包成 .exe 运行时生效）"""
    try:
        if sys.stdout is None or sys.stderr is None:
            console = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(console, win32con.SW_HIDE)
    except (win32gui.error, WindowsError) as e:
        print(f"隐藏控制台失败: {e}")

def main():
    if not check_single_instance():
        app = QApplication(sys.argv)
        QMessageBox.warning(None, "提示", "程序已在运行中！")
        return 1
    
    hide_console_window()
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    pet.destroyed.connect(app.quit)
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
