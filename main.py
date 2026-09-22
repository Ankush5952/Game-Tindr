import sys
from PySide6.QtWidgets import QApplication, QWidget

from core.database import init_db, get_session
from core.models import User
from config.settings import Settings
from utils.logger import get_logger
from sources.registry import SourceRegistry
from core.game_repository import save_game

#Init logger
logger = get_logger(__name__)

#User initialize
def ensure_default_user() -> None:
    '''
    Creates the User row if it doesn't exist
    '''
    session = get_session()
    try:
        existing_user = session.query(User).first()
        if existing_user is None:
            new_user = User(display_name = "Player")
            session.add(new_user)
            session.commit()
            logger.info("Created Default user")
        else:
            logger.info(f"Using existing user : {existing_user.display_name}")
    finally:
        session.close()

#Game saving
def fetch_and_save_games() -> None:
    '''
    Fetches game from active sources and saves new ones to db
    '''


    settings = Settings.load()
    registry = SourceRegistry(settings)
    session = get_session()
    try:
        for source in registry.get_active_sources():
            games = source.fetch_games(limit = 10)
            for raw_game in games:
                save_game(session, raw_game)
    finally:
        session.close()

#Main function
def main() -> None:
    logger.info("Starting Game Tindr")

    settings = Settings.load()
    logger.info(f"Loaded settings - active theme : {settings.active_theme}")

    init_db()
    ensure_default_user()

    fetch_and_save_games()

    
    #Manages whole GUI app - handles event loop
    app = QApplication(sys.argv)

    #base class for anything visual
    window = QWidget()
    window.setWindowTitle("Game Tindr - Phase 2")
    window.resize(400, 300)
    window.show()

    #closes the app with the right exit code
    sys.exit(app.exec())

if __name__ == "__main__":
    main()