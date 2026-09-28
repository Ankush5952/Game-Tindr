import logging
from pathlib import Path

from utils.paths import get_app_data_path

LOG_FILE = get_app_data_path()/"game_tindr.log"

def get_logger(name : str) -> logging.Logger:
    '''
    Returns a configured logger
    Call at the start of any module that needs to log something, passing name for log-message
    '''

    logger = logging.getLogger(name)
    
    #Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

    #Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    #File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding = "utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

