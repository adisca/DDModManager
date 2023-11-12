from PySide2.QtGui import QPalette, QColor, QFont
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QGroupBox

from ui.FlowLayout import FlowLayout
from logic.Mod import Mod


class ModStatusTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._initialize()

    def _initialize(self) -> None:
        vbox = QVBoxLayout()

        generalBox = QGroupBox("General", self)
        self.vboxGeneralData = QVBoxLayout()
        generalBox.setLayout(self.vboxGeneralData)
        vbox.addWidget(generalBox)

        widgetTags = QGroupBox("Tags", self)
        self.flowTags = FlowLayout()
        widgetTags.setLayout(self.flowTags)
        vbox.addWidget(widgetTags)

        self.setLayout(vbox)

    def loadMod(self, mod: Mod) -> None:
        if not mod.metadata:
            print(f"Mod {mod.id} {mod.name} has no metadata to show")
            return

        for i in reversed(range(self.vboxGeneralData.count())):
            self.vboxGeneralData.takeAt(i).widget().deleteLater()
        self.vboxGeneralData.addWidget(QLabel(mod.metadata.name))
        authorsTxt = ""
        for author in mod.metadata.authors:
            authorsTxt += f"{author}\n"
        self.vboxGeneralData.addWidget(QLabel(authorsTxt))

        for i in reversed(range(self.flowTags.count())):
            self.flowTags.takeAt(i).widget().deleteLater()
        for tag in mod.metadata.tags:
            self.flowTags.addWidget(TagBubble(tag))
        self.flowTags.refresh()


class TagBubble(QLabel):
    def __init__(self, text: str):
        new_text = text.title()
        super(TagBubble, self).__init__(new_text)

        self.word = new_text
        self.setContentsMargins(5, 5, 5, 5)

        self.setFont(QFont('Times', 15))
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(140, 140, 140))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.adjustSize()
