from PySide6.QtWidgets import *
import sys

class MainWidget(QWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('main widget')
        self.move(300,300)
        self.resize(400,200)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget()
    sys.exit(app.exec())