import logging
import colorlog
from constants.paths import LOG_FILE


def init_logger():
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()  # Logs to console
    file_handler = logging.FileHandler(LOG_FILE)  # Logs to a file

    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)

    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] - %(levelname)-8s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'purple',
        }
    )
    console_handler.setFormatter(console_formatter)

    file_formatter = logging.Formatter(
        "[%(asctime)s] - %(levelname)-8s - %(filename)s | %(lineno)d | %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


logger = logging.getLogger("CustomLogger")
