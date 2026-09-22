import json
from multiprocessing.pool import TERMINATE
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)

THEMES_DIR = Path(__file__).resolve().parent/"themes"
TEMPLATE_PATH = THEMES_DIR/"template.qss"

def load_stylesheet(theme_name : str) -> str:
    '''
    Loads a theme's colorpalletes ans subs them
    in a shared QSS template
    '''

    palette_path = THEMES_DIR/f"{theme_name}.json"
    if not palette_path.exists():
        logger.warning(f"Theme '{theme_name}' not found, falling back to 'dark'")
        palette_path = THEMES_DIR/"dark.json"

    with open(palette_path, 'r') as f:
        palette = json.load(f)

    with open(TEMPLATE_PATH, 'r') as f:
        template = f.read()

    stylesheet = template
    for color_name, color_val in palette.items():
        stylesheet = stylesheet.replace(f"${color_name}", color_val)

    return stylesheet