from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QMainWindow


class ModInfoTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.desc = QWebEngineView(self)
        self.desc.setHtml('<body style="background-color:black;"></body>')

        self.setCentralWidget(self.desc)

    def loadMod(self, mod):
        print(f"Loading page for: {mod.id} {mod.name}")
        if mod.metadata:
            self.desc.setHtml(mod.metadata.desc)
        else:
            print(f"Mod {mod.id} has no metadata")
