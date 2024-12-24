from typing import Union, List
import logic.dd_stuff as dd_stuff
from threading import RLock
from constants.pathsImgs import *
from shared.signals import signal_manager


class DLC:
    def __init__(self, _id: str, name: str, title: str, img: str):
        self.id = _id
        self.name = name
        self.title = title
        self.img = img


class SubDLC:
    def __init__(self, name: str, title: str, parent_dlc: DLC, img: str):
        self.name = name
        self.title = title
        self.dlc = parent_dlc
        self.img = img


class _DlcListSingleton(object):
    DLC_BC = DLC("1117860", "arena_mp", "The Butcher's Circus", HEADER_BC_IMG)
    DLC_MSK = DLC("445700", "musketeer", "The Musketeer", HEADER_MSK_IMG)
    DLC_CC = DLC("580100", "crimson_court", "The Crimson Court", HEADER_CC_IMG)
    DLC_SB = DLC("702540", "shieldbreaker", "The Shieldbreaker", HEADER_SB_IMG)
    DLC_COM = DLC("735730", "color_of_madness", "The Color Of Madness", HEADER_COM_IMG)

    DLC_UNKNOWN = DLC("0", "unknown", "Unknown", PLACEHOLDER_IMG)

    list: List[DLC] = []

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


class _SubDlcListSingleton(object):
    SUB_DLC_BC = SubDLC("arena_mp", DlcList.DLC_BC.title, DlcList.DLC_BC, HEADER_BC_IMG)
    SUB_DLC_MSK = SubDLC("musketeer", DlcList.DLC_MSK.title, DlcList.DLC_MSK, HEADER_MSK_IMG)
    SUB_DLC_CC = SubDLC("crimson_court", DlcList.DLC_CC.title, DlcList.DLC_CC, HEADER_CC_IMG)
    SUB_DLC_DIS = SubDLC("districts", "Districts", DlcList.DLC_CC, HEADER_CC_IMG)
    SUB_DLC_FLG = SubDLC("flagellant", "Flagellant", DlcList.DLC_CC, HEADER_CC_IMG)
    SUB_DLC_SB = SubDLC("shieldbreaker", DlcList.DLC_SB.title, DlcList.DLC_SB, HEADER_SB_IMG)
    SUB_DLC_COM = SubDLC("color_of_madness", DlcList.DLC_COM.title, DlcList.DLC_COM, HEADER_COM_IMG)

    SUB_DLC_UNKNOWN = SubDLC("unknown", "Unknown", DlcList.DLC_UNKNOWN, PLACEHOLDER_IMG)

    list: List[SubDLC] = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_SubDlcListSingleton, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.list.append(self.SUB_DLC_BC)
        self.list.append(self.SUB_DLC_MSK)
        self.list.append(self.SUB_DLC_CC)
        self.list.append(self.SUB_DLC_DIS)
        self.list.append(self.SUB_DLC_FLG)
        self.list.append(self.SUB_DLC_SB)
        self.list.append(self.SUB_DLC_COM)

    def getByName(self, name: str, default: type = SUB_DLC_UNKNOWN) -> Union[SubDLC, type]:
        for subDlc in self.list:
            if subDlc.name == name:
                return subDlc
        return default

    def getByParent(self, dlc: DLC) -> List[SubDLC]:
        result = []
        for subDlc in self.list:
            if subDlc.dlc.name == dlc.name:
                result.append(subDlc)
        return result


SubDlcList = _SubDlcListSingleton()


class _DlcDBSingleton(object):
    ownedDlc: List[DLC] = []
    activeDlc: List[SubDLC] = []

    _lock = RLock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(_DlcDBSingleton, cls).__new__(cls)
            return cls.instance

    def initialize(self) -> None:
        self.reload()

    def reload(self) -> None:
        with self._lock:
            self.clear()
            self.ownedDlc, self.activeDlc = dd_stuff.getDlcs()
        signal_manager.s_dlcs_reloaded.emit()

    def clear(self) -> None:
        with self._lock:
            self.ownedDlc.clear()
            self.activeDlc.clear()


DlcDB = _DlcDBSingleton()
