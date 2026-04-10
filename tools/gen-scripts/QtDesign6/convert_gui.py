import sys
from PyQt6 import QtWidgets, uic
# pyuic6 mainwindow.ui -o MainWindow.py
from MainWindow import Ui_MainWindow

app = QtWidgets.QApplication(sys.argv)

window = uic.loadUi("mainwindow.ui")
window.show()
app.exec()
