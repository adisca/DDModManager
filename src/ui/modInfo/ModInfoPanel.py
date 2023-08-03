from PySide2.QtWidgets import QTabWidget, QScrollArea

from ui.modInfo.ModBrowserTab import ModBrowserTab
from ui.modInfo.ModDescriptionTab import ModDescriptionTab
from ui.modInfo.ModRequirementsTab import ModRequirementsTab
from ui.modInfo.ModStatusTab import ModStatusTab


class ModInfoScreen(QTabWidget):
    selected_mod = None

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

    def loadMod(self, mod):
        if not mod:
            print("No mod to load")
            return

        print(f"Loading info for: {mod.id} {mod.name}")

        if mod != self.selected_mod:
            self.selected_mod = mod
            self.statusPanel.loadMod(mod)
            self.reqTab.loadMod(mod)
            self.descTab.loadMod(mod)

    def redirectToBrowser(self, url):
        self.setCurrentWidget(self.browserTab)
        self.browserTab.load(url)
