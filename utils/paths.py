import sys
from pathlib import Path

def get_base_path() -> Path:
    '''
    Returns the folder that read-only bundled resources live in
    -Dev : project root
    -Prod : temp MEIPASS folder
    '''
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent.parent

def get_app_data_path() -> Path:
    '''
    Returns the folder where the writable data should live in
    Dev : project root
    Prod : folder where .exe file is
    '''
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent
