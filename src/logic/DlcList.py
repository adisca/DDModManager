from typing import Union

from constants.pathsImgs import *


class DLC:
    def __init__(self, _id: str, name: str, title: str, img: str):
        self.id = _id
        self.name = name
        self.title = title
        self.img = img


class _DlcListSingleton(object):
    DLC_BC = DLC("1117860", "arena_mp", "The Butcher's Circus", HEADER_BC_IMG)
    DLC_MSK = DLC("445700", "musketeer", "The Musketeer", HEADER_MSK_IMG)
    DLC_CC = DLC("580100", "crimson_court", "The Crimson Court", HEADER_CC_IMG)
    DLC_SB = DLC("702540", "shieldbreaker", "The Shieldbreaker", HEADER_SB_IMG)
    DLC_COM = DLC("735730", "color_of_madness", "The Color Of Madness", HEADER_COM_IMG)

    DLC_UNKNOWN = DLC("0", "unknown", "Unknown", PLACEHOLDER_IMG)

    list: list[DLC] = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_DlcListSingleton, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.list.append(self.DLC_BC)
        self.list.append(self.DLC_MSK)
        self.list.append(self.DLC_CC)
        self.list.append(self.DLC_SB)
        self.list.append(self.DLC_COM)

    def getById(self, _id: str, default: type = DLC_UNKNOWN) -> Union[DLC, type]:
        for dlc in self.list:
            if dlc.id == _id:
                return dlc
        return default

    def getByName(self, name: str, default: type = DLC_UNKNOWN) -> Union[DLC, type]:
        for dlc in self.list:
            if dlc.name == name:
                return dlc
        return default


DlcList = _DlcListSingleton()
