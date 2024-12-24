import io
import os
from typing import Callable, List

import dotenv

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QFileDialog, QGridLayout, QPushButton, QLabel, QLineEdit, \
    QComboBox, QVBoxLayout, QGroupBox, QHBoxLayout, QDialog, QScrollArea, QMessageBox

from constants.paths import *
from logic import dd_stuff
from src.shared.signals import signal_manager
from logic.DlcDB import DlcDB, SubDlcList, SubDLC
from shared.logger import logger
from ui.dlcManagement.DlcItem import DlcItem


class DlcWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DLCs")
        self.setGeometry(200, 100, 580, 850)

        self._createLayout()

    def _createLayout(self) -> None:
        mainLayout = QVBoxLayout()

        self.dlcLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()

        dlcGroup = QGroupBox()
        actionsGroup = QGroupBox()
        actionsGroup.setFixedHeight(50)

        dlcGroup.setLayout(self.dlcLayout)
        actionsGroup.setLayout(hboxLayout)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(dlcGroup)

        mainLayout.addWidget(scroll)
        mainLayout.addWidget(actionsGroup)

        # Action Buttons Group
        button = QPushButton("Save", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onSave)
        hboxLayout.addWidget(button)

        button = QPushButton("Enable all", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onEnableAll)
        hboxLayout.addWidget(button)

        button = QPushButton("Disable all", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onDisableAll)
        hboxLayout.addWidget(button)

        button = QPushButton("Close", self)
        button.setFixedWidth(100)
        button.clicked.connect(self._onClose)
        hboxLayout.addWidget(button)

        self.setLayout(mainLayout)

        self._loadDLC()

    def _loadDLC(self) -> None:
        DlcDB.reload()
        for dlc in DlcDB.ownedDlc:
            for subDlc in SubDlcList.getByParent(dlc):
                self.dlcLayout.addWidget(DlcItem(subDlc))

    def _onSave(self) -> None:
        logger.debug("Save changes")
        try:
            dd_stuff.writeDlcAndSave(self.getItemsData())
            DlcDB.reload()
        except FileNotFoundError:
            QMessageBox(QMessageBox.Icon.Critical, "Error", "Decrypted game file is missing").exec_()
        except io.UnsupportedOperation:
            QMessageBox(QMessageBox.Icon.Critical, "Error", "Could not read or write decrypted game file").exec_()
        except Exception as err:
            QMessageBox(QMessageBox.Icon.Critical, "Error", str(err)).exec_()
        self.close()

    def _onEnableAll(self) -> None:
        for i in range(self.dlcLayout.count()):
            self.dlcLayout.itemAt(i).widget().setDlcEnabled(True)

    def _onDisableAll(self) -> None:
        for i in range(self.dlcLayout.count()):
            self.dlcLayout.itemAt(i).widget().setDlcEnabled(False)

    def _onClose(self) -> None:
        self.close()

    def getItemsData(self) -> List[SubDLC]:
        subDlcs = []
        for i in range(self.dlcLayout.count()):
            widget = self.dlcLayout.itemAt(i).widget()
            if widget.isActive:
                subDlcs.append(widget.subDlc)
        return subDlcs
