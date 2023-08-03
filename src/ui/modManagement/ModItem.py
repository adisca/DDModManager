from PySide2.QtCore import Qt, QMimeData, Signal
from PySide2.QtGui import QDrag, QPixmap, QPalette, QColor, QFont, QFontMetrics
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel

from constants.pathsImgs import *


class ModItem(QWidget):
    SIZE_W = 500
    SIZE_H = 110

    IMG_W = 100
    IMG_H = SIZE_H - 10

    clicked = Signal(object)

    def __init__(self, mod):
        super().__init__()
        self.mod = mod

        self._initialize()

    def _initialize(self):
        self.setFixedSize(self.SIZE_W, self.SIZE_H)
        self.setToolTip(f"ID: {self.mod.id}\nSource: {self.mod.source}\nActive: {self.mod.active}")

        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        hbox.setContentsMargins(5, 5, 5, 5)

        labelImg = QLabel(self)
        img = QPixmap((PLACEHOLDER_IMG if (self.mod.img is None) else self.mod.img))
        img = img.scaled(self.IMG_W, self.IMG_H, Qt.KeepAspectRatio)
        labelImg.setPixmap(img)
        labelImg.setMargin(0)
        hbox.addWidget(labelImg)

        labelName = QLabel(self.mod.name, self)
        labelName.setMargin(0)
        font = QFont('Times', 15)
        fm = QFontMetrics(font)
        labelName.setFont(font)
        labelName.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if fm.width(self.mod.name) > 0:
            labelName.setFixedWidth(self.SIZE_W - self.IMG_W - 10)
            labelName.setWordWrap(True)

        hbox.addWidget(labelName)

        hbox.addStretch(0)

        self.setLayout(hbox)

        self.refreshBackgroundColor()

    def refreshBackgroundColor(self):
        palette = self.palette()

        if not self.mod.installed:
            # palette.setColor(QPalette.Window, QColor(255, 169, 162))
            palette.setColor(QPalette.Window, QColor(140, 0, 0))
        elif self.mod.active:
            # palette.setColor(QPalette.Window, QColor(144, 238, 144))
            palette.setColor(QPalette.Window, QColor(0, 100, 0))
        else:
            palette.setColor(QPalette.Window, QColor(140, 140, 140))

        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def mouseReleaseEvent(self, e):
        print("Click ", end="")
        print(self.mod.toString())
        self.clicked.emit(self)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

    def getData(self):
        return self.mod
