
class ModMetadata:
    def __init__(self, mod_id, name, tags, desc, req_dlc=None, req_mods=None):
        if req_mods is None:
            req_mods = []
        if req_dlc is None:
            req_dlc = []

        self.id = mod_id
        self.name = name
        self.tags = tags
        self.desc = desc
        self.req_dlc = req_dlc
        self.req_mods = req_mods

    def toList(self):
        return [self.id, self.name, self.tags, self.desc, self.req_dlc, self.req_mods]
