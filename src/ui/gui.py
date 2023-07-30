import sys

from PySide2.QtGui import QIcon, QColor, QPalette
from PySide2.QtWidgets import QApplication, QMainWindow, QAction
from PySide2.QtCore import Qt

from ui.ModTab import ModTab
from ui.SettingsWindow import SettingsWindow
from ui.PreferencesWindow import PreferencesWindow
from constants.paths import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DD Mod Manager")
        self.setGeometry(300, 200, 1500, 700)
        self.setWindowIcon(QIcon(PLACEHOLDER_IMG))

        self.createMenus()
        self.modTab = ModTab()
        self.setCentralWidget(self.modTab)

    def createMenus(self):
        menuBar = self.menuBar()
        settingsMenu = menuBar.addMenu(QIcon(), "Settings")

        pathSettingsAction = QAction(QIcon(), "Paths", self)
        pathSettingsAction.triggered.connect(self.openPathSettingsDialog)
        settingsMenu.addAction(pathSettingsAction)

        preferencesAction = QAction(QIcon(), "Preferences", self)
        preferencesAction.triggered.connect(self.openPreferencesDialog)
        settingsMenu.addAction(preferencesAction)

    def openPathSettingsDialog(self):
        dialog = SettingsWindow()
        dialog.changedSettings.connect(self.modTab.reload)
        dialog.exec_()

    def openPreferencesDialog(self):
        dialog = PreferencesWindow()
        dialog.exec_()


def run():
    app = QApplication(sys.argv)

    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
