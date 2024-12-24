from typing import Optional

from PySide2.QtWidgets import QTabWidget, QScrollArea
from PySide2.QtCore import QUrl

from ui.modInfo.ModBrowserTab import ModBrowserTab
from ui.modInfo.ModDescriptionTab import ModDescriptionTab
from ui.modInfo.ModRequirementsTab import ModRequirementsTab
from ui.modInfo.ModStatusTab import ModStatusTab
from logic.Mod import Mod
from shared.logger import logger


class ModInfoScreen(QTabWidget):
    selected_mod: Optional[Mod] = None

    def __init__(self):
        super().__init__()

        self.statusPanel = ModStatusTab(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.statusPanel)

        self.descTab = ModDescriptionTab(self)
        self.descTab.denied_nav_req.connect(self.redirectToBrowser)

        self.reqTab = ModRequirementsTab(self)

        self.browserTab = ModBrowserTab(self)

        self.addTab(scroll, "Status")
        self.addTab(self.reqTab, "Reqs")
        self.addTab(self.descTab, "Desc")
        self.addTab(self.browserTab, "Browser")

    def loadMod(self, mod: Mod) -> None:
        if not mod:
            logger.warn("No mod to load")
            return

        logger.debug(f"Loading info for: {mod.id} {mod.name}")

        if mod != self.selected_mod:
            self.selected_mod = mod
            self.statusPanel.loadMod(mod)
            self.reqTab.loadMod(mod)
            self.descTab.loadMod(mod)

    # Only required required tab can change, at least for now
    def reloadMod(self) -> None:
        if self.selected_mod:
            self.reqTab.loadMod(self.selected_mod)

    def clean(self) -> None:
        self.selected_mod = None
        self.statusPanel.clear()
        self.reqTab.clear()
        self.descTab.clear()

    def redirectToBrowser(self, url: QUrl) -> None:
        self.setCurrentWidget(self.browserTab)
        self.browserTab.load(url)
