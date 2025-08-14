import sys
from PySide6.QtWidgets import QApplication
from src.pet_window import DesktopPet

def main():
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

# 目前的bug是，在右键单击关闭之后，python程序不会退出