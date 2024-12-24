import os
import csv
import json
import traceback
from typing import List, Tuple

from bs4 import BeautifulSoup

from logic.Mod import Mod, ModSources
from logic.SaveManager import SaveFileManager
import logic.util as util
from logic.CacheModMetadata import metadataCache
import logic.scrapper as scrapper
from logic.ModMetadata import ModMetadata
from logic.DlcDB import DLC, SubDLC, DlcList, SubDlcList
from constants.paths import *
from shared.logger import logger
from shared.signals import signal_manager


def get_mods_from_folder(mod_dir_path: str, source: ModSources = ModSources.Local) -> List[Mod]:
    mods = []
    for dir_name in next(os.walk(mod_dir_path))[1]:
        dir_path = os.path.join(mod_dir_path, dir_name)
        for file in next(os.walk(dir_path))[2]:
            if file == "project.xml":
                file_path = os.path.join(dir_path, file)
                with open(file_path, "r", encoding="utf8") as f:
                    file_contents = f.read()
                bs_data = BeautifulSoup(file_contents, "xml")

                try:
                    mod_id = bs_data.find("PublishedFileId").text
                    mod_name = bs_data.find("Title").text
                except Exception:
                    logger.error(
                        f"Mod id or name could not be read from fields PublishedFileId, Title respectively. Path: {dir_path}")
                    traceback.print_exc()
                    continue

                mod_img_xml = bs_data.find("PreviewIconFile")
                if mod_img_xml:
                    mod_img = mod_img_xml.text
                else:
                    mod_img = None

                mod_desc_xml = bs_data.find("ItemDescription")
                if mod_desc_xml:
                    mod_desc = mod_desc_xml.text
                else:
                    mod_desc = ""

                mod_tags = []
                mod_tag_group_xml = bs_data.find("Tags")
                if mod_tag_group_xml:
                    mod_tags_xml = mod_tag_group_xml.find_all("Tags")

                    if not len(mod_tags_xml):
                        logger.debug(f"Mod {mod_id} {mod_name} has a tag container but no tags")
                    else:
                        for tag_xml in mod_tags_xml:
                            if tag_xml.text:
                                mod_tags.append(tag_xml.text.title())
                            else:
                                logger.debug(f"Mod {mod_id} {mod_name} has an empty tag")
                else:
                    logger.debug(f"Mod {mod_id} {mod_name} has no tags")

                ok = True
                if source == ModSources.Local and mod_name in [x.name for x in mods]:
                    ok = False
                    logger.debug(f"Duplicate name for local mod: {mod_id} {mod_name}")
                elif source == ModSources.Steam and mod_id in [x.id for x in mods]:
                    ok = False
                    logger.debug(f"Duplicate id for steam mod: {mod_id} {mod_name}")

                if ok:
                    mods.append(Mod(
                        mod_id,
                        mod_name,
                        source,
                        mod_img=(f"{dir_path}/{mod_img}" if mod_img else None),
                        desc=mod_desc,
                        tags=mod_tags
                    ))
                break
    return mods


def get_enabled_mods_data(json_data: dict) -> List[Tuple[str, str]]:
    mods_data = []

    if "applied_ugcs_1_0" in json_data["base_root"]:
        for entry in json_data["base_root"]["applied_ugcs_1_0"]:
            mods_data.append(
                (
                    json_data["base_root"]["applied_ugcs_1_0"][entry]["name"],
                    json_data["base_root"]["applied_ugcs_1_0"][entry]["source"]
                )
            )

    return mods_data


# ignores duplicate ids, the first is written
def exportModlist(path: str, mods: List[Mod]) -> None:
    exportedList = []
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.writer(f, delimiter=',')
        for mod in mods:
            if mod.installed and mod.id not in exportedList:
                csv_writer.writerow([mod.id])
                exportedList.append(mod.id)
            else:
                logger.debug(f"Duplicate or not installed in export: {mod.id}")


def importCsvModlist(modlist_path: str, installed_mods: List[Mod]):
    return importModlist(read_modlist_csv(modlist_path), installed_mods)


def importURLModlist(modlist_url: str, installed_mods: List[Mod]):
    return importModlist(scrapper.get_mods_from_collection(modlist_url), installed_mods)


def importModlist(modlist_ids: List[str], installed_mods: List[Mod]) -> (List[Mod], List[Mod], List[Mod], List[Mod]):
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
def read_modlist_csv(modlist_path: str) -> List[str]:
    res = []
    with open(modlist_path, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[0].isdigit() and row[0] not in res:
                res.append(row[0])
            else:
                logger.debug(f"Duplicate or bad id mod in import: {row[0]}")
        f.close()
    return res


def convert_mod_list_to_json_mods(mods: List[Mod]) -> dict[str, dict[str, str]]:
    res = {}
    for i, mod in enumerate(mods):
        if mod.installed:
            res[f"{i}"] = {"name": (mod.id if mod.source == ModSources.Steam else mod.name), "source": mod.source}
    return res


def writeModsToGameFile(decryptedGameFile: str, mods: List[Mod]) -> None:
    with open(decryptedGameFile, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        json_data["base_root"]["applied_ugcs_1_0"] = convert_mod_list_to_json_mods(mods)
        # json_data["base_root"]["persistent_ugcs"]["applied_ugcs_1_0"] = json_data["base_root"]["applied_ugcs_1_0"]

    with open(decryptedGameFile, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def writeModsAndSave(mods: List[Mod]) -> None:
    sfm = SaveFileManager(os.environ["SAVE_EDITOR_JAR_PATH"], os.environ["SAVES_FOLDER"], os.environ["PROFILE"])
    writeModsToGameFile(TARGET_JSON, mods)
    sfm.encrypt_save_info(TARGET_JSON, GAME_FILE_NAME)


def convert_dlc_list_to_json_dlcs(dlcs: List[SubDLC]) -> dict[str, dict[str, str]]:
    res = {}
    for i, dlc in enumerate(dlcs):
        res[f"{i}"] = {"name": dlc.name, "source": "dlc"}
    return res


def writeDlcToGameFile(decryptedGameFile: str, dlcs: List[SubDLC]) -> None:
    with open(decryptedGameFile, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        json_data["base_root"]["dlc"] = convert_dlc_list_to_json_dlcs(dlcs)

    with open(decryptedGameFile, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)


def writeDlcAndSave(dlcs: List[SubDLC]) -> None:
    sfm = SaveFileManager(os.environ["SAVE_EDITOR_JAR_PATH"], os.environ["SAVES_FOLDER"], os.environ["PROFILE"])
    writeDlcToGameFile(TARGET_JSON, dlcs)
    sfm.encrypt_save_info(TARGET_JSON, GAME_FILE_NAME)


def getAllMods() -> List[Mod]:
    _, _, disabled_mods, enabled_mods = getCategorisedMods()
    return enabled_mods + disabled_mods


def getOwnedDlc(json_data: dict) -> List[DLC]:
    dlc_data: List[DLC] = []
    if "presented_dlc" in json_data["base_root"] and "dlc" in json_data["base_root"]["presented_dlc"]:
        for entry in json_data["base_root"]["presented_dlc"]["dlc"]:
            dlc_data.append(
                    DlcList.getByName(json_data["base_root"]["presented_dlc"]["dlc"][entry]["name"])
            )
    return dlc_data


def getEnabledDlc(json_data: dict) -> List[SubDLC]:
    dlc_data: List[SubDLC] = []
    if "dlc" in json_data["base_root"]:
        for entry in json_data["base_root"]["dlc"]:
            dlc_data.append(
                    SubDlcList.getByName(json_data["base_root"]["dlc"][entry]["name"])
            )
    return dlc_data


def getDlcs() -> (List[DLC], List[SubDLC]):
    if "SAVES_FOLDER" in os.environ and os.path.exists(os.environ["SAVES_FOLDER"]):
        SaveFileManager(os.environ["SAVE_EDITOR_JAR_PATH"], os.environ["SAVES_FOLDER"],
                        os.environ["PROFILE"]).decrypt_save_info(TARGET_JSON, GAME_FILE_NAME)
        with open(TARGET_JSON, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        return getOwnedDlc(json_data), getEnabledDlc(json_data)


def getCategorisedMods() -> (List[Mod], List[Mod], List[Mod], List[Mod]):
    installed_mods = []

    if "GAME_FOLDER" in os.environ and os.path.exists(os.environ["GAME_FOLDER"]):
        installed_mods = get_mods_from_folder(util.mods_path(os.environ["GAME_FOLDER"]), ModSources.Local)
    else:
        logger.warn("Game local mods folder not found")

    if "MODS_FOLDER_STEAM" in os.environ and os.path.exists(os.environ["MODS_FOLDER_STEAM"]):
        installed_mods = installed_mods + get_mods_from_folder(os.environ["MODS_FOLDER_STEAM"], ModSources.Steam)
    else:
        logger.warn("Steam mods folder not found")

    if len(installed_mods) == 0:
        logger.warn("No installed mods found")

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
                    deleted_mod = Mod(mod_name if mod_name.isdigit() else "0", mod_name, mod_source, installed=False)
                    enabled_mods.append(deleted_mod)
                    uninstalled_mods.append(deleted_mod)
        except Exception as err:
            logger.error(err)

        for mod in enabled_mods:
            if mod in disabled_mods:
                disabled_mods.remove(mod)

    getFromCache(installed_mods, uninstalled_mods)

    return installed_mods, uninstalled_mods, disabled_mods, enabled_mods


def getFromCache(installed_mods: List[Mod], uninstalled_mods: List[Mod]) -> None:
    for list_mods in [installed_mods, uninstalled_mods]:
        for uncached_mod in metadataCache.retrieveModsMetadata(list_mods):
            signal_manager.s_loading_mods.emit(uncached_mod.toString())
            if uncached_mod.id and uncached_mod.id != "0":
                mod_data = scrapper.get_mod_info_by_id(uncached_mod.id)
                if mod_data:
                    uncached_mod.setMetadata(ModMetadata(*mod_data))
                    metadataCache.addToCache([uncached_mod.metadata])
    metadataCache.saveCache()
