from PySide2.QtCore import Qt, QMimeData, Signal
from PySide2.QtGui import QDrag, QPixmap, QPalette, QColor, QFont, QFontMetrics, QMouseEvent
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsOpacityEffect, QCheckBox

from constants.pathsImgs import *
from logic.DlcDB import SubDLC, DlcDB
from shared.logger import logger


class DlcItem(QWidget):
    SIZE_W = 500
    SIZE_H = 110

    IMG_W = 200
    IMG_H = SIZE_H - 10

    isActive = False

    def __init__(self, subDlc: SubDLC):
        super().__init__()
        self.subDlc = subDlc

        self.filtered = False

        self._initialize()

    def _initialize(self) -> None:
        self.setFixedSize(self.SIZE_W, self.SIZE_H)
        # self.setToolTip(f"ID: {self.subDlc.name}\nSource: {self.subDlc.dlc.}\nActive: {self.subDlc.active}")

        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        hbox.setContentsMargins(5, 5, 5, 5)

        labelImg = QLabel(self)
        img = QPixmap((PLACEHOLDER_IMG if (self.subDlc.img is None) else self.subDlc.img))
        img = img.scaled(self.IMG_W, self.IMG_H, Qt.KeepAspectRatio)
        labelImg.setPixmap(img)
        labelImg.setMargin(0)
        hbox.addWidget(labelImg)

        labelName = QLabel(self.subDlc.title, self)
        labelName.setMargin(0)
        font = QFont('Times', 15)
        fm = QFontMetrics(font)
        labelName.setFont(font)
        labelName.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if fm.width(self.subDlc.name) > 0:
            labelName.setFixedWidth(self.SIZE_W - self.IMG_W - 10)
            labelName.setWordWrap(True)

        hbox.addWidget(labelName)

        hbox.addStretch(0)

        self.activeImg = QLabel(self)
        self.activeImg.setAlignment(Qt.AlignRight)
        self.activeImg.setMargin(0)
        hbox.addWidget(self.activeImg)

        self.setLayout(hbox)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(140, 140, 140))

        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.setDlcEnabled(self.subDlc in DlcDB.activeDlc)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        logger.debug(f"Click {self.subDlc.name}")
        self.setDlcEnabled(not self.isActive)

    def setDlcEnabled(self, isActive: bool) -> None:
        self.isActive = isActive

        if isActive:
            img = QPixmap(CHECK_IMG)
        else:
            img = QPixmap(CROSS_IMG)
        img = img.scaled(self.IMG_W, self.IMG_H, Qt.KeepAspectRatio)
        self.activeImg.setPixmap(img)
