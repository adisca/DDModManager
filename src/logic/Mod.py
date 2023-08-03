
IMG_SIZE = (50, 50)


class ModSources:
    Steam = "Steam"
    Local = "mod_local_source"
    Unknown = ""


class Mod:
    def __init__(self, mod_id, mod_name, source, mod_img=None, desc="", tags=None, active=False, installed=True, metadata=None):
        if tags is None:
            tags = []

        self.id = mod_id
        self.name = mod_name
        self.source = source
        self.img = mod_img
        self.desc = desc
        self.tags = tags
        self.active = active
        self.installed = installed
        self.metadata = metadata

    def setMetadata(self, metadata):
        self.metadata = metadata
        self.name = metadata.name

    def toString(self):
        return f"{self.id} {self.name}"
