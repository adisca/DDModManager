from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from logic.Mod import Mod
from logic.DlcList import DlcList
from logic.CacheModMetadata import metadataCache
from ui.modInfo.ModRequirementItem import ModRequirementItem


class ModRequirementsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._initialize()

    def _initialize(self):
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
            print(f"Mod {mod.id} {mod.name} has no metadata to show")
            return

        for i in reversed(range(self.vboxRequiredDLC.count())):
            self.vboxRequiredDLC.takeAt(i).widget().deleteLater()
        for dlc in mod.metadata.req_dlc:
            self.vboxRequiredDLC.addWidget(ModRequirementItem(DlcList.getById(dlc).title))

        for i in reversed(range(self.vboxRequiredMods.count())):
            self.vboxRequiredMods.takeAt(i).widget().deleteLater()
        for req_mod in mod.metadata.req_mods:
            self.vboxRequiredMods.addWidget(ModRequirementItem(metadataCache.getById(req_mod, {"name": req_mod}).name))
