import logic.dd_stuff as dd_stuff


class _ModDBSingleton(object):
    cachedMods = []
    installedMods = []
    uninstalledMods = []
    disabledMods = []
    enabledMods = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_ModDBSingleton, cls).__new__(cls)
        return cls.instance

    def initialize(self):
        self.reload()

    def loadCsvModlist(self, modlist_path):
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods =\
            dd_stuff.importCsvModlist(modlist_path, self.installedMods)

    def loadURLModlist(self, modlist_url):
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods =\
            dd_stuff.importURLModlist(modlist_url, self.installedMods)

    def reload(self):
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = dd_stuff.getCategorisedMods()

    def dump(self):
        return self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods

    def clear(self):
        self.installedMods = []
        self.uninstalledMods = []
        self.disabledMods = []
        self.enabledMods = []

    def loadCache(self):
        self.cachedMods.clear()

    def saveCache(self):
        pass


# exportable singleton
ModDB = _ModDBSingleton()
