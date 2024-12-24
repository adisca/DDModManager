from typing import Union, List

from bs4 import BeautifulSoup
import requests
import re

import logic.util as util
from shared.logger import logger


STEAM_CSS_TAGS = '''<link href="https://community.cloudflare.steamstatic.com/public/shared/css/motiva_sans.css?v=GfSjbGKcNYaQ&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/shared/css/buttons.css?v=uR_4hRD_HUln&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/shared/css/shared_global.css?v=eMNk5XNDdT3l&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/globalv2.css?v=RL7hpFRFPE4A&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/shared/css/apphub.css?v=pdN-za99ZT1T&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/skin_1/forums.css?v=gMNxlzV7kVGo&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/skin_1/workshop.css?v=jJRp21N3avd9&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/skin_1/workshop_itemdetails.css?v=z9wX1u2fep5E&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/skin_1/friendpicker.css?v=.WDBc9u4THCvp&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/skin_1/modalContent.css?v=.TP5s6TzX6LLh&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/applications/community/main.css?v=Syg4u7us6Uuf&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/shared/css/shared_responsive.css?v=KrKRjQbCfNh0&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/shared/css/apphub_images.css?v=_0CllnFpmuY6&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >
<link href="https://community.cloudflare.steamstatic.com/public/css/skin_1/header.css?v=vh4BMeDcNiCU&amp;l=romanian&amp;_cdn=cloudflare" rel="stylesheet" type="text/css" >'''


def get_mods_from_collection(url: str) -> List[str]:
    logger.debug(f"Get mods from collection: {url}")

    mod_ids = []

    page = requests.get(url)
    if not page:
        raise Exception("Failed to load the collection page")

    bs = BeautifulSoup(page.content, "html.parser")
    results = bs.find_all(class_="collectionItem")
    if not results:
        raise Exception("No results found, are you sure this is the right page?")

    for result in results:
        mod_ids.append(result.get("id").replace("sharedfile_", ""))

    logger.info(f"Mods extracted from collection, {len(mod_ids)} mods were found")

    return mod_ids


def get_mod_info(url: str) -> (str, str, List[str], List[str], List[str], List[str]):
    logger.info(f"Getting mod info from: {url}")

    page = requests.get(url)
    if not page:
        raise Exception

    bs = BeautifulSoup(page.content, "html.parser")

    _id = "0"
    url_numbers = re.findall(r"\d+", url)
    if url_numbers:
        _id = url_numbers[0]

    title = bs.find(class_="workshopItemTitle")
    if not title:
        return

    # description = bs.find(class_="workshopItemDescription")
    # description = add_tags_to_body(add_steam_css(create_empty_html()), [description])

    required_dlcs = []
    for dlc in bs.find_all(class_="requiredDLCItem"):
        dlc_hyperlink = dlc.find("a")
        if dlc_hyperlink:
            required_dlcs.append(re.findall(r"\d+", dlc_hyperlink["href"])[0])

    required_mods = []
    required_mods_container = bs.find(class_="requiredItemsContainer")
    if required_mods_container:
        for req_mod in required_mods_container.find_all("a"):
            required_mods.append(re.findall(r"\d+", req_mod["href"])[0])

    tags = []
    for tag_group in bs.find_all(class_="workshopTags"):
        for tag in tag_group.find_all("a"):
            tags.append(tag.text.lower())

    authors = []
    for author in bs.find_all(class_="friendBlockContent"):
        authors.append(author.contents[0].strip())

    return _id, title.text, tags, authors, required_dlcs, required_mods


def get_mod_info_by_id(mod_id: str) -> (str, str, List[str], List[str], List[str], List[str]):
    return get_mod_info(util.mod_page_url(mod_id))


def create_empty_html() -> BeautifulSoup:
    return BeautifulSoup("<!DOCTYPE html><html><head></head><body></body></html>", "html.parser")


def add_tags_to_head(doc: BeautifulSoup, tags: Union[BeautifulSoup, List[BeautifulSoup]]) -> BeautifulSoup:
    for tag in tags:
        doc.find("head").append(tag)
    return doc


def add_tags_to_body(doc: BeautifulSoup, tags: Union[BeautifulSoup, List[BeautifulSoup]]) -> BeautifulSoup:
    for tag in tags:
        doc.find("body").append(tag)
    return doc


def add_steam_css(doc: BeautifulSoup) -> BeautifulSoup:
    return add_tags_to_head(doc, BeautifulSoup(STEAM_CSS_TAGS, "html.parser"))
