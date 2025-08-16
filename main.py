import sys
from PySide6.QtWidgets import QApplication
from src.pet_window import DesktopPet

def main():
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    pet.destroyed.connect(app.quit)
    return_value = app.exec()
    sys.exit(return_value)

if __name__ == '__main__':
    main()
