import os
import ctypes

from ui.gui import run
import dotenv
from logic.ModDB import ModDB
from logic.CacheModMetadata import metadataCache
from constants.paths import *


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Dev mode
    os.chdir("..")

    os.environ["APP_PATH"] = os.getcwd()

    myAppId = u"DDModManager"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppId)

    dotenv.load_dotenv(ENV_FILE)

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(TARGET_JSON), exist_ok=True)
    os.makedirs(MODLISTS_FOLDER, exist_ok=True)

    metadataCache.loadCache()
    ModDB.initialize()

    run()
