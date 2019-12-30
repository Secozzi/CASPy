from PyQt5 import QtCore, QtGui, QtWidgets

from CAS import Ui_MainWindow
import os
import traceback

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.consoleIn.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.consoleIn and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                self.consoleIn.appendPlainText("... ")
                return True
        return super(MainWindow, self).eventFilter(obj, event)


if __name__ == "__main__":
    import sys
    def excepthook(exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("error catched!:")
        print("error message:\n", tb)
        QtWidgets.QApplication.quit()
    sys.excepthook = excepthook
    e = Ui_MainWindow()
    print("Debug mode")
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())