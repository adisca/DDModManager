from PySide2.QtCore import Qt, QMimeData, Signal
from PySide2.QtGui import QDrag, QPixmap, QPalette, QColor, QFont, QFontMetrics, QImage, QIcon
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel

from constants.pathsImgs import *


class ModRequirementStates:
    Unfulfilled = 0
    Incomplete = 1
    Fulfilled = 2


class ModRequirementItem(QWidget):
    SIZE_W = 300
    SIZE_H = 70

    IMG_W = 50
    IMG_H = 50

    def __init__(self, name: str, fulfilled: ModRequirementStates = ModRequirementStates.Unfulfilled):
        super().__init__()

        self.setFixedSize(self.SIZE_W, self.SIZE_H)

        hbox = QHBoxLayout()

        self.nameLabel = QLabel(self)
        self.nameLabel.setMargin(0)
        self.nameLabel.setFont(QFont('Times', 12))
        self.nameLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hbox.addWidget(self.nameLabel)

        self.labelImg = QLabel(self)
        self.labelImg.setAlignment(Qt.AlignRight)
        self.labelImg.setMargin(0)
        hbox.addWidget(self.labelImg)

        self.setLayout(hbox)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(140, 140, 140))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.setData(name, fulfilled)

    def setData(self, name: str, fulfilled: ModRequirementStates = ModRequirementStates.Unfulfilled) -> None:
        self.nameLabel.setText(name)
        fm = QFontMetrics(self.nameLabel.font())
        if fm.width(name) > 0:
            self.nameLabel.setFixedWidth(self.SIZE_W - self.IMG_W - 10)
            self.nameLabel.setWordWrap(True)

        if fulfilled == ModRequirementStates.Fulfilled:
            img = QPixmap(CHECK_IMG)
        elif fulfilled == ModRequirementStates.Incomplete:
            img = QPixmap(EXCLAMATION_IMG)
        else:
            img = QPixmap(CROSS_IMG)
        img = img.scaled(self.IMG_W, self.IMG_H, Qt.KeepAspectRatio)
        self.labelImg.setPixmap(img)

        # self.refreshBackgroundColor()

    # def refreshBackgroundColor(self):
    #     palette = self.palette()
    #
    #     if not self.mod.installed:
    #         palette.setColor(QPalette.Window, QColor(140, 0, 0))
    #     elif self.mod.active:
    #         palette.setColor(QPalette.Window, QColor(0, 100, 0))
    #     else:
    #         palette.setColor(QPalette.Window, QColor(140, 140, 140))
    #
    #     self.setPalette(palette)
    #     self.setAutoFillBackground(True)
