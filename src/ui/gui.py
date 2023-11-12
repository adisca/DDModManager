import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QAction

from ui.visuals.DarkPalette import DarkPalette
from constants.pathsImgs import *
from ui.ModTab import ModTab
from ui.menus.PreferencesWindow import PreferencesWindow
from ui.menus.SettingsWindow import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DD Mod Manager")
        self.setGeometry(300, 200, 1500, 700)
        self.setWindowIcon(QIcon(PLACEHOLDER_IMG))

        self._createMenus()
        self.modTab = ModTab()
        self.setCentralWidget(self.modTab)

    def _createMenus(self) -> None:
        menuBar = self.menuBar()
        settingsMenu = menuBar.addMenu(QIcon(), "Settings")

        pathSettingsAction = QAction(QIcon(), "Paths", self)
        pathSettingsAction.triggered.connect(self.openPathSettingsDialog)
        settingsMenu.addAction(pathSettingsAction)

        preferencesAction = QAction(QIcon(), "Preferences", self)
        preferencesAction.triggered.connect(self.openPreferencesDialog)
        settingsMenu.addAction(preferencesAction)

    def openPathSettingsDialog(self) -> None:
        dialog = SettingsWindow()
        dialog.changedSettings.connect(self.modTab.reload)
        dialog.exec_()

    def openPreferencesDialog(self) -> None:
        dialog = PreferencesWindow()
        dialog.exec_()


def run() -> None:
    app = QApplication(sys.argv)

    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
    app.setPalette(DarkPalette())

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
