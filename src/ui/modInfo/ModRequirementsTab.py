from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from logic.Mod import Mod
from logic.DlcDB import DlcList, DlcDB
from logic.CacheModMetadata import metadataCache
from shared.signals import signal_manager
from ui.dlcManagement.DlcWindow import DlcWindow
from ui.modInfo.ModRequirementItem import ModRequirementItem, ModRequirementStates
from shared.logger import logger
from logic.ModDB import ModDB


class ModRequirementsTab(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._initialize()

    def _initialize(self) -> None:
        vbox = QVBoxLayout()

        widgetRequiredDLC = QGroupBox("Required DLC", self)
        self.vboxRequiredDLC = QVBoxLayout()
        self.vboxRequiredDLC.setAlignment(Qt.AlignTop)
        widgetRequiredDLC.setLayout(self.vboxRequiredDLC)
        vbox.addWidget(widgetRequiredDLC)

        widgetRequiredMods = QGroupBox("Required Mods", self)
        self.vboxRequiredMods = QVBoxLayout()
        self.vboxRequiredMods.setAlignment(Qt.AlignTop)
        widgetRequiredMods.setLayout(self.vboxRequiredMods)
        vbox.addWidget(widgetRequiredMods)

        self.setLayout(vbox)

    def loadMod(self, mod: Mod) -> None:
        if not mod.metadata:
            logger.warn(f"Mod {mod.id} {mod.name} has no metadata to show")
            return

        self.clear()

        for dlc in mod.metadata.req_dlc:
            for enabled_dlc in DlcDB.activeDlc:
                if enabled_dlc.dlc.id == dlc:
                    status = ModRequirementStates.Fulfilled
                    break
            else:
                for owned_dlc in DlcDB.ownedDlc:
                    if owned_dlc.id == dlc:
                        status = ModRequirementStates.Incomplete
                        break
                else:
                    status = ModRequirementStates.Unfulfilled
            dlcReqItem = ModRequirementItem(DlcList.getById(dlc).title, status)
            dlcReqItem.clicked.connect(self.openDlcWindow)
            self.vboxRequiredDLC.addWidget(dlcReqItem)

        for req_mod in mod.metadata.req_mods:
            for enabled_mod in ModDB.enabledMods:
                if enabled_mod.id == req_mod:
                    status = ModRequirementStates.Fulfilled
                    break
            else:
                for disabled_mod in ModDB.disabledMods:
                    if disabled_mod.id == req_mod:
                        status = ModRequirementStates.Incomplete
                        break
                else:
                    status = ModRequirementStates.Unfulfilled
            modReqItem = ModRequirementItem(metadataCache.getById(req_mod, {"name": req_mod}).name, status)
            modReqItem.clicked.connect(self.searchForMod)
            self.vboxRequiredMods.addWidget(modReqItem)

    def clear(self) -> None:
        for i in reversed(range(self.vboxRequiredDLC.count())):
            self.vboxRequiredDLC.takeAt(i).widget().deleteLater()
        for i in reversed(range(self.vboxRequiredMods.count())):
            self.vboxRequiredMods.takeAt(i).widget().deleteLater()

    @staticmethod
    def openDlcWindow(_: str) -> None:
        DlcWindow().exec_()

    @staticmethod
    def searchForMod(name: str) -> None:
        signal_manager.s_set_name_filter.emit(name)
