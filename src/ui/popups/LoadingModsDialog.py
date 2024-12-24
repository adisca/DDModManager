from PySide2.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PySide2.QtCore import Qt

from src.shared.signals import signal_manager


class LoadingModsDialog(QDialog):
    DEFAULT_TEXT = "Loading mods..."

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading Mods")
        self.setModal(True)  # Makes the dialog modal (blocks interaction with other windows)

        # Setup layout and widgets
        layout = QVBoxLayout()
        self.label = QLabel(self.DEFAULT_TEXT)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)

        self.setFixedSize(800, 60)

        layout.addWidget(self.label)
        self.setLayout(layout)

        signal_manager.s_loading_mods.connect(self.update_status)

    def update_status(self, mod_name):
        self.label.setText(f"Loading:\n{mod_name}")

    def close(self) -> bool:
        self.label.setText(self.DEFAULT_TEXT)
        return super().close()
