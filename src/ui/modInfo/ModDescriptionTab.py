from PySide2.QtCore import Signal, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from bs4 import BeautifulSoup

import logic.scrapper as scrapper
import logic.util as util


class ModDescriptionTab(QWebEngineView):
    denied_nav_req = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._initialize()

    def _initialize(self):
        self.setPage(SafeDescPage(self))
        self.page().denied_nav_req.connect(self.denied_nav_req.emit)
        self.setHtml('<body style="background-color:black;"></body>')
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def loadMod(self, mod):
        self.setHtml(str(scrapper.add_tags_to_body(scrapper.add_steam_css(scrapper.create_empty_html()),
                                                   [BeautifulSoup(util.convert_bbcode_to_html(mod.desc),
                                                                  "html.parser")])))


class SafeDescPage(QWebEnginePage):
    denied_nav_req = Signal(object)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeBackForward:
            return False

        if _type not in [QWebEnginePage.NavigationType.NavigationTypeTyped,
                         QWebEnginePage.NavigationType.NavigationTypeReload]:
            print(f"Nav request denied: {_type} {isMainFrame} {url}\n")
            self.denied_nav_req.emit(url)
            return False

        return True
