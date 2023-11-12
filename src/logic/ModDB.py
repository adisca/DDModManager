from typing import List, Set, Optional

import logic.dd_stuff as dd_stuff
from logic.Mod import Mod


class _ModDBSingleton(object):
    allMods: List[Mod] = []
    installedMods: List[Mod] = []
    uninstalledMods: List[Mod] = []
    disabledMods: List[Mod] = []
    enabledMods: List[Mod] = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_ModDBSingleton, cls).__new__(cls)
        return cls.instance

    def initialize(self) -> None:
        self.reload()

    def loadCsvModlist(self, modlist_path: str) -> None:
        self.clear()
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = \
            dd_stuff.importCsvModlist(modlist_path, self.installedMods)
        self.allMods = self.enabledMods + self.disabledMods

    def loadURLModlist(self, modlist_url: str) -> None:
        self.clear()
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = \
            dd_stuff.importURLModlist(modlist_url, self.installedMods)
        self.allMods = self.enabledMods + self.disabledMods

    def reload(self) -> None:
        self.clear()
        self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = dd_stuff.getCategorisedMods()
        self.allMods = self.enabledMods + self.disabledMods

    def dump(self):
        return self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods

    def clear(self) -> None:
        self.installedMods.clear()
        self.uninstalledMods.clear()
        self.disabledMods.clear()
        self.enabledMods.clear()
        self.allMods.clear()

    def getAllTags(self) -> List[str]:
        tags_set: Set[Optional[str]] = set()
        for mod in self.allMods:
            if mod.tags:
                tags_set.update(mod.tags)

        tags_list = list(tags_set)
        tags_list.sort()
        return tags_list


# exportable singleton
ModDB = _ModDBSingleton()
