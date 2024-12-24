import os
import ctypes

from ui.gui import run
import dotenv
from logic.ModDB import ModDB
from logic.CacheModMetadata import metadataCache
from constants.paths import *
from shared.logger import init_logger


def init_dirs():
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(TARGET_JSON), exist_ok=True)
    os.makedirs(MODLISTS_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Dev mode
    os.chdir("..")

    os.environ["APP_PATH"] = os.getcwd()

    myAppId = u"DDModManager"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppId)

    dotenv.load_dotenv(ENV_FILE)

    init_dirs()
    init_logger()

    metadataCache.loadCache()
    # ModDB.initialize()

    run()
