import csv
import os
import ast

from logic.ModMetadata import ModMetadata

from constants.paths import *


class _MetadataCacheSingleton:
    cache = []
    _hasChanged = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_MetadataCacheSingleton, cls).__new__(cls)
        return cls.instance

    def getById(self, meta_id, default=None):
        return next((m for m in self.cache if m.id == meta_id), default)

    def loadCache(self):
        self.cache = []

        if not os.path.exists(CACHE_PATH):
            open(CACHE_PATH, "w", encoding="utf-8").close()

        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                self.cache.append(self.convertCsvRowToModMetadata(row))
        print("Mod metadata cache loaded")

    def saveCache(self):
        if self._hasChanged:
            with open(CACHE_PATH, "w", newline="", encoding="utf-8") as f:
                csv_writer = csv.writer(f, delimiter=',')
                for metadata in self.cache:
                    csv_writer.writerow(metadata.toList())
            print("Mod metadata cache saved")
            _hasChanged = False

    def addToCache(self, metadatas):
        cacheIds = [m.id for m in self.cache]
        for metadata in metadatas:
            if metadata.id not in cacheIds:
                self.cache.append(metadata)
                self._hasChanged = True

    def retrieveModsMetadata(self, mods):
        uncachedMods = []
        for mod in mods:
            meta = next((m for m in self.cache if m.id == mod.id or m.name == mod.name), None)
            if meta:
                mod.setMetadata(meta)
            else:
                uncachedMods.append(mod)
        return uncachedMods

    @staticmethod
    def convertCsvRowToModMetadata(row):
        return ModMetadata(
            row[0],
            row[1],
            ast.literal_eval(row[2]),
            ast.literal_eval(row[3]),
            ast.literal_eval(row[4]),
            ast.literal_eval(row[5])
        )


# exportable singleton
metadataCache = _MetadataCacheSingleton()