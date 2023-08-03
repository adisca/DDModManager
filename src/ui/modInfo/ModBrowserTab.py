from urllib.parse import urlparse

from PySide2.QtCore import QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class ModBrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._initialize()

    def _initialize(self) -> None:
        self.setPage(SteamOnlyPage(self))
        self.load(QUrl("https://steamcommunity.com/app/262060/workshop/"))


class SteamOnlyPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if urlparse(url.url()).netloc != "steamcommunity.com"\
                or urlparse(url.url()).path.split("/")[1] in ["login", "market"]:
            return False
        return True
