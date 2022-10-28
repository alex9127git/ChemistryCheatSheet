import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from main_window import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fill_reaction_btn.clicked.connect(self.fill_reaction)

    def fill_reaction(self):
        reagent1 = self.primary_input_edit.text()
        reagent2 = self.secondary_input_edit.text()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())
