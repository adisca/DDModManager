from typing import List, Set, Optional

import logic.dd_stuff as dd_stuff
from logic.Mod import Mod
from threading import RLock
from shared.logger import logger


class _ModDBSingleton(object):
    allMods: List[Mod] = []
    installedMods: List[Mod] = []
    uninstalledMods: List[Mod] = []
    disabledMods: List[Mod] = []
    enabledMods: List[Mod] = []

    _lock = RLock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(_ModDBSingleton, cls).__new__(cls)
            return cls.instance

    def initialize(self) -> None:
        self.reload()

    def loadCsvModlist(self, modlist_path: str) -> None:
        with self._lock:
            self.clear()
            self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = \
                dd_stuff.importCsvModlist(modlist_path, self.installedMods)
            self.allMods = self.enabledMods + self.disabledMods

    def loadURLModlist(self, modlist_url: str) -> None:
        with self._lock:
            self.clear()
            self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = \
                dd_stuff.importURLModlist(modlist_url, self.installedMods)
            self.allMods = self.enabledMods + self.disabledMods

    def reload(self) -> None:
        with self._lock:
            self.clear()
            self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods = dd_stuff.getCategorisedMods()
            self.allMods = self.enabledMods + self.disabledMods

    def dump(self):
        return self.installedMods, self.uninstalledMods, self.disabledMods, self.enabledMods

    def clear(self) -> None:
        with self._lock:
            self.installedMods.clear()
            self.uninstalledMods.clear()
            self.disabledMods.clear()
            self.enabledMods.clear()
            self.allMods.clear()

    def moveMod(self, mod_id: str, column: str, changed_column: bool, index: int) -> None:
        if column == 'enabled':
            if changed_column:
                mod = next((mod for mod in self.disabledMods if mod.id == mod_id), None)
                if not mod:
                    logger.error(f"Mod {mod_id} not found in disabled list")
                    return
                self.disabledMods.remove(mod)
            else:
                mod = next((mod for mod in self.enabledMods if mod.id == mod_id), None)
                if not mod:
                    logger.error(f"Mod {mod_id} not found in enabled list")
                    return
                self.enabledMods.remove(mod)
            self.enabledMods.insert(index, mod)
        elif column == 'disabled':
            if changed_column:
                mod = next((mod for mod in self.enabledMods if mod.id == mod_id), None)
                if not mod:
                    logger.error(f"Mod {mod_id} not found in enabled list")
                    return
                self.enabledMods.remove(mod)
                self.disabledMods.insert(index, mod)
        pass

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
