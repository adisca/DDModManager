import os
import csv
import json

from bs4 import BeautifulSoup

from logic.Mod import Mod, ModSources
from logic.SaveManager import SaveFileManager
import logic.util as util
from logic.cacheModMetadata import MetadataCache
import logic.scrapper as scrapper
from logic.ModMetadata import ModMetadata
from constants.paths import *


def get_mods_from_folder(mod_dir_path, source=ModSources.Local):
    mods = []
    for dir_name in next(os.walk(mod_dir_path))[1]:
        dir_path = os.path.join(mod_dir_path, dir_name)
        for file in next(os.walk(dir_path))[2]:
            if file == "project.xml":
                file_path = os.path.join(dir_path, file)
                with open(file_path, "r", encoding="utf8") as f:
                    file_contents = f.read()
                bs_data = BeautifulSoup(file_contents, "xml")

                mod_id = bs_data.find("PublishedFileId").text
                mod_name = bs_data.find("Title").text

                ok = True
                if source == ModSources.Local and mod_name in [x.name for x in mods]:
                    ok = False
                    print(f"Duplicate name for local mod: {mod_id} {mod_name}")
                elif source == ModSources.Steam and mod_id in [x.id for x in mods]:
                    ok = False
                    print(f"Duplicate id for steam mod: {mod_id} {mod_name}")

                if ok:
                    mods.append(Mod(
                        mod_id,
                        mod_name,
                        source,
                        f'{dir_path}/{bs_data.find("PreviewIconFile").text}'
                    ))
                break
    return mods


def get_enabled_mods_data(json_data):
    mods = []

    if "applied_ugcs_1_0" in json_data["base_root"]:
        for entry in json_data["base_root"]["applied_ugcs_1_0"]:
            mods.append(
                (
                    json_data["base_root"]["applied_ugcs_1_0"][entry]["name"],
                    json_data["base_root"]["applied_ugcs_1_0"][entry]["source"]
                )
            )

    return mods


def get_mods_names(mod_dir_path):
    mods = []
    for dir_name in next(os.walk(mod_dir_path))[1]:
        dir_path = os.path.join(mod_dir_path, dir_name)
        for file in next(os.walk(dir_path))[2]:
            if file == "project.xml":
                file_path = os.path.join(dir_path, file)
                with open(file_path, "r", encoding="utf8") as f:
                    file_contents = f.read()
                bs_data = BeautifulSoup(file_contents, "xml")
                mods.append(bs_data.find("Title").text)
                break
    return mods


# ignores duplicate ids, the first is written
def exportModlist(path, mods):
    exportedList = []
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.writer(f, delimiter=',')
        for mod in mods:
            if mod.installed and mod.id not in exportedList:
                csv_writer.writerow([mod.id])
                exportedList.append(mod.id)
            else:
                print(f"Duplicate or not installed in export: {mod.id}")


def importCsvModlist(modlist_path, installed_mods):
    return importModlist(read_modlist_csv(modlist_path), installed_mods)


def importURLModlist(modlist_url, installed_mods):
    return importModlist(scrapper.get_mods_from_collection(modlist_url), installed_mods)


def importModlist(modlist_ids, installed_mods):
    new_installed_mods = installed_mods.copy()
    uninstalled_mods = []
    disabled_mods = installed_mods.copy()
    enabled_mods = []

    for mod_id in modlist_ids:
        mod = next((x for x in new_installed_mods if x.id == mod_id),
                   Mod(mod_id, mod_id, ModSources.Unknown, active=False, installed=False))

        if mod not in enabled_mods:
            enabled_mods.append(mod)
            if not mod.installed:
                uninstalled_mods.append(mod)

    for mod in enabled_mods:
        if mod in disabled_mods:
            disabled_mods.remove(mod)

    getFromCache([], uninstalled_mods)

    return new_installed_mods, uninstalled_mods, disabled_mods, enabled_mods


# ignores duplicate ids, the first is taken
def read_modlist_csv(modlist_path):
    res = []
    with open(modlist_path, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[0].isdigit() and row[0] not in res:
                res.append(row[0])
            else:
                print(f"Duplicate or bad id mod in import: {row[0]}")
        f.close()
    return res


def convert_mod_list_to_json_mods(mods):
    res = {}
    for i, mod in enumerate(mods):
        if mod.installed:
            res[f"{i}"] = {"name": (mod.id if mod.source == ModSources.Steam else mod.name), "source": mod.source}
    return res


def writeModsToGameFile(decryptedGameFile, mods):
    with open(decryptedGameFile, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        json_data["base_root"]["applied_ugcs_1_0"] = convert_mod_list_to_json_mods(mods)
        # json_data["base_root"]["persistent_ugcs"]["applied_ugcs_1_0"] = json_data["base_root"]["applied_ugcs_1_0"]

    with open(decryptedGameFile, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def writeModsAndSave(mods):
    sfm = SaveFileManager(os.environ["SAVE_EDITOR_JAR_PATH"], os.environ["SAVES_FOLDER"], os.environ["PROFILE"])
    writeModsToGameFile(TARGET_JSON, mods)
    sfm.encrypt_save_info(TARGET_JSON, GAME_FILE_NAME)


def getCategorisedMods():
    installed_mods = []

    if "GAME_FOLDER" in os.environ and os.path.exists(os.environ["GAME_FOLDER"]):
        installed_mods = get_mods_from_folder(util.mods_path(os.environ["GAME_FOLDER"]), ModSources.Local)
    else:
        print("Game local mods folder not found")

    if "MODS_FOLDER_STEAM" in os.environ and os.path.exists(os.environ["MODS_FOLDER_STEAM"]):
        installed_mods = installed_mods + get_mods_from_folder(os.environ["MODS_FOLDER_STEAM"], ModSources.Steam)
    else:
        print("Steam mods folder not found")

    if len(installed_mods) == 0:
        print("No installed mods found")

    disabled_mods = installed_mods.copy()
    enabled_mods = []
    uninstalled_mods = []
    if "SAVES_FOLDER" in os.environ and os.path.exists(os.environ["SAVES_FOLDER"]):
        try:
            SaveFileManager(os.environ["SAVE_EDITOR_JAR_PATH"], os.environ["SAVES_FOLDER"],
                            os.environ["PROFILE"]).decrypt_save_info(TARGET_JSON, GAME_FILE_NAME)
            with open(TARGET_JSON, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            enabled_mods_data = get_enabled_mods_data(json_data)

            for mod_name, mod_source in enabled_mods_data:
                is_installed = False
                if mod_source == ModSources.Local:
                    for mod in installed_mods:
                        if mod_name == mod.name and mod_source == mod.source:
                            mod.active = True
                            enabled_mods.append(mod)
                            is_installed = True
                            break
                elif mod_source == ModSources.Steam:
                    for mod in installed_mods:
                        if mod_name == mod.id and mod_source == mod.source:
                            mod.active = True
                            enabled_mods.append(mod)
                            is_installed = True
                            break
                if not is_installed:
                    deleted_mod = Mod(0, mod_name, mod_source, installed=False)
                    enabled_mods.append(deleted_mod)
                    uninstalled_mods.append(deleted_mod)
        except Exception as err:
            print(err)

        for mod in enabled_mods:
            if mod in disabled_mods:
                disabled_mods.remove(mod)

    getFromCache(installed_mods, uninstalled_mods)

    return installed_mods, uninstalled_mods, disabled_mods, enabled_mods


def getFromCache(installed_mods, uninstalled_mods):
    for uncached_mod in MetadataCache.retrieveModsMetadata(installed_mods):
        uncached_mod.setMetadata(ModMetadata(*scrapper.get_mod_info_by_id(uncached_mod.id)))
        MetadataCache.addToCache([uncached_mod.metadata])
    for uncached_mod in MetadataCache.retrieveModsMetadata(uninstalled_mods):
        if uncached_mod.id:
            uncached_mod.setMetadata(ModMetadata(*scrapper.get_mod_info_by_id(uncached_mod.id)))
            MetadataCache.addToCache([uncached_mod.metadata])
    MetadataCache.saveCache()

