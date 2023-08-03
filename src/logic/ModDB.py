import logic.dd_stuff as dd_stuff
from logic.Mod import Mod


class _ModDBSingleton(object):
    installedMods: list[Mod] = []
    uninstalledMods: list[Mod] = []
    disabledMods: list[Mod] = []
    enabledMods: list[Mod] = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_ModDBSingleton, cls).__new__(cls)
        return cls.instance

    def initialize(self) -> None:
        self.reload()

    def loadCsvModlist(self, modlist_path: str) -> None:
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods =\
            dd_stuff.importCsvModlist(modlist_path, self.installedMods)

    def loadURLModlist(self, modlist_url: str) -> None:
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods =\
            dd_stuff.importURLModlist(modlist_url, self.installedMods)

    def reload(self) -> None:
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = dd_stuff.getCategorisedMods()

    def dump(self):
        return self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods

    def clear(self) -> None:
        self.installedMods = []
        self.uninstalledMods = []
        self.disabledMods = []
        self.enabledMods = []


# exportable singleton
ModDB = _ModDBSingleton()
