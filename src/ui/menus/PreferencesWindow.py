from PySide2.QtWidgets import QDialog, QPushButton, QHBoxLayout, QGroupBox, QVBoxLayout


class PreferencesWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Preferences settings")
        self.setGeometry(300, 200, 500, 300)

        self._createLayout()

    def _createLayout(self) -> None:
        vboxLayout = QVBoxLayout()

        actionsGroup = QGroupBox()
        actionsGroup.setFixedHeight(50)

        hboxLayout = QHBoxLayout()

        button = QPushButton("Close", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onSettingsClose)
        hboxLayout.addWidget(button)

        actionsGroup.setLayout(hboxLayout)

        vboxLayout.addWidget(actionsGroup)

        self.setLayout(vboxLayout)

    def _onSettingsClose(self):
        self.close()
