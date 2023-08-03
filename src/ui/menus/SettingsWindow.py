import os
import dotenv

from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QFileDialog, QGridLayout, QPushButton, QLabel, QLineEdit,\
    QComboBox, QVBoxLayout, QGroupBox, QHBoxLayout, QDialog

from constants.paths import *


class SettingsWindow(QDialog):
    changedSettings = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Paths settings")
        self.setGeometry(300, 200, 500, 300)

        self.createLayout()

    def createLayout(self):
        vboxLayout = QVBoxLayout()

        gridLayout = QGridLayout()
        hboxLayout = QHBoxLayout()

        settingsGroup = QGroupBox()
        actionsGroup = QGroupBox()
        actionsGroup.setFixedHeight(50)

        # Row 0
        row = 0
        col = 0

        label = QLabel("Saves editor:", self)
        gridLayout.addWidget(label, row, col)
        col += 1

        self.txtSaveEditorJar = QLineEdit((os.environ["SAVE_EDITOR_JAR_PATH"] if "SAVE_EDITOR_JAR_PATH" in os.environ else ""), self)
        gridLayout.addWidget(self.txtSaveEditorJar, row, col)
        col += 1

        button = QPushButton("Browse", self)
        button.clicked.connect(self.browseFileExplorerForFile(self.txtSaveEditorJar, file_filter="JAR File (*.jar)"))
        gridLayout.addWidget(button, row, col)
        col += 1

        # Row 1
        row += 1
        col = 0

        label = QLabel("Game Folder:", self)
        gridLayout.addWidget(label, row, col)
        col += 1

        self.txtGameFolder = QLineEdit((os.environ["GAME_FOLDER"] if "GAME_FOLDER" in os.environ else ""), self)
        gridLayout.addWidget(self.txtGameFolder, row, col)
        col += 1

        button = QPushButton("Browse", self)
        button.clicked.connect(self.browseFileExplorerForFolder(self.txtGameFolder))
        gridLayout.addWidget(button, row, col)
        col += 1

        # Row 2
        row += 1
        col = 0

        label = QLabel("Mods Folder (Steam):", self)
        gridLayout.addWidget(label, row, col)
        col += 1

        self.txtModsFolderSteam = QLineEdit((os.environ["MODS_FOLDER_STEAM"] if "MODS_FOLDER_STEAM" in os.environ else ""), self)
        gridLayout.addWidget(self.txtModsFolderSteam, row, col)
        col += 1

        button = QPushButton("Browse", self)
        button.clicked.connect(self.browseFileExplorerForFolder(self.txtModsFolderSteam))
        gridLayout.addWidget(button, row, col)
        col += 1

        # Row 3
        row += 1
        col = 0

        label = QLabel("Saves Folder:", self)
        gridLayout.addWidget(label, row, col)
        col += 1

        self.txtSavesFolder = QLineEdit((os.environ["SAVES_FOLDER"] if "SAVES_FOLDER" in os.environ else ""), self)
        gridLayout.addWidget(self.txtSavesFolder, row, col)
        col += 1

        button = QPushButton("Browse", self)
        button.clicked.connect(self.browseFileExplorerForFolder(self.txtSavesFolder))
        gridLayout.addWidget(button, row, col)
        col += 1

        # Row 4
        row += 1
        col = 0

        label = QLabel("Profile", self)
        gridLayout.addWidget(label, row, col)
        col += 1

        self.comboProfile = QComboBox(self)
        self.comboProfile.addItems([str(x) for x in range(0, 9)])
        try:
            self.comboProfile.setCurrentIndex(int(os.environ["PROFILE"]))
        except:
            pass
        gridLayout.addWidget(self.comboProfile, row, col)
        col += 1

        settingsGroup.setLayout(gridLayout)

        # Action Buttons Group
        button = QPushButton("Save", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onSettingsSave)
        hboxLayout.addWidget(button)

        button = QPushButton("Apply", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onSettingsApply)
        hboxLayout.addWidget(button)

        button = QPushButton("Close", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onSettingsClose)
        hboxLayout.addWidget(button)

        actionsGroup.setLayout(hboxLayout)

        # Vbox With Everything
        vboxLayout.addWidget(settingsGroup)
        vboxLayout.addWidget(actionsGroup)

        self.setLayout(vboxLayout)

    def browseFileExplorerForFolder(self, target, window_name="File Explorer"):
        def browse():
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.DirectoryOnly)

            path = dialog.getExistingDirectory(self, QObject.tr(self, window_name), target.text())
            if path:
                target.setText(path)

        return browse

    def browseFileExplorerForFile(self, target, window_name="File Explorer", file_filter="All Files (*)"):
        def browse():
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.AnyFile)

            path, _ = dialog.getOpenFileName(self, QObject.tr(self, window_name),  target.text(), QObject.tr(self, file_filter))
            if path:
                target.setText(path)

        return browse

    def _onSettingsSave(self):
        os.environ["SAVE_EDITOR_JAR_PATH"] = self.txtSaveEditorJar.text()
        os.environ["GAME_FOLDER"] = self.txtGameFolder.text()
        os.environ["MODS_FOLDER_STEAM"] = self.txtModsFolderSteam.text()
        os.environ["SAVES_FOLDER"] = self.txtSavesFolder.text()
        os.environ["PROFILE"] = self.comboProfile.currentText()

        dotenv.set_key(ENV_FILE, "SAVE_EDITOR_JAR_PATH", os.environ["SAVE_EDITOR_JAR_PATH"])
        dotenv.set_key(ENV_FILE, "GAME_FOLDER", os.environ["GAME_FOLDER"])
        dotenv.set_key(ENV_FILE, "MODS_FOLDER_STEAM", os.environ["MODS_FOLDER_STEAM"])
        dotenv.set_key(ENV_FILE, "SAVES_FOLDER", os.environ["SAVES_FOLDER"])
        dotenv.set_key(ENV_FILE, "PROFILE", os.environ["PROFILE"])

        self.changedSettings.emit()

        self.close()

    def _onSettingsApply(self):
        os.environ["SAVE_EDITOR_JAR_PATH"] = self.txtSaveEditorJar.text()
        os.environ["GAME_FOLDER"] = self.txtGameFolder.text()
        os.environ["MODS_FOLDER_STEAM"] = self.txtModsFolderSteam.text()
        os.environ["SAVES_FOLDER"] = self.txtSavesFolder.text()
        os.environ["PROFILE"] = self.comboProfile.currentText()

        self.changedSettings.emit()

        self.close()

    def _onSettingsClose(self):
        self.close()
