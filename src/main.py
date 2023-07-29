from src.ui.gui import run
import dotenv
from src.logic.ModDB import ModDB
from src.logic.cacheModMetadata import MetadataCache
from src.constants.paths import *

if __name__ == '__main__':
    dotenv.load_dotenv(ENV_FILE)

    MetadataCache.loadCache()
    ModDB.initialize()

    run()
