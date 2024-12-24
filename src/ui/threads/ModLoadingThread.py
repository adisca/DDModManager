from PySide2.QtCore import QThread, Signal

from logic.DlcDB import DlcDB
from logic.ModDB import ModDB
from shared.logger import logger


class ModLoadingThread(QThread):
    mod_loading_finished = Signal()  # Signal to update the UI

    def __init__(self):
        super().__init__()

    def run(self) -> None:
        try:
            logger.debug("Reloading mod db")
            ModDB.reload()
            logger.debug("Reloading dlc db")
            DlcDB.reload()
            logger.debug("Done reloading")

            self.mod_loading_finished.emit()
        except Exception as err:
            logger.error(err)
