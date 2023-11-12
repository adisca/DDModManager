from typing import Optional, List

from logic.ModMetadata import ModMetadata


class ModSources:
    Steam = "Steam"
    Local = "mod_local_source"
    Unknown = ""


class Mod:
    def __init__(self, mod_id: str, mod_name: str, source: ModSources, mod_img: Optional[str] = None, desc: str = "",
                 tags: List[str] = None, active: bool = False, installed: bool = True,
                 metadata: Optional[ModMetadata] = None):
        if tags is None:
            tags = []

        self.id = mod_id
        self.name = mod_name
        self.source = source
        self.img = mod_img
        self.desc = desc
        self.tags: List[str] = tags
        self.active = active
        self.installed = installed
        self.metadata = metadata

    def setMetadata(self, metadata: ModMetadata) -> None:
        self.metadata = metadata
        self.name = metadata.name

    def toString(self) -> str:
        return f"{self.id} {self.name}"
