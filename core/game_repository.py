from sqlalchemy.orm import Session

from core.models import Game, Genre
from sources.base_source import RawGameData
from utils.logger import get_logger

logger = get_logger(__name__)

def get_or_create_genre(session : Session, genre_name : str) -> Genre:
    '''
    Looks up Genre by name, creating it if it doesn't exist yet
    '''
    genre = session.query(Genre).filter_by(name = genre_name).first()
    if genre is None:
        genre = Genre(name = genre_name)
        session.add(genre)

    return genre

def save_game(session : Session, raw : RawGameData) -> Game:
    '''
    Saves a RawGameData into the database as a Game row
    skips saving if already exists
    '''

    existing = (
        session.query(Game)
        .filter_by(source_name = raw.source_name, source_id = raw.source_id)
        .first()
        )

    if existing:
        existing.title = raw.title
        existing.description = raw.description
        existing.cover_image_url = raw.cover_image_url
        existing.release_year =raw.release_year

        existing.genres = [ get_or_create_genre(session, name) for name in raw.genres ]
        logger.info(f"Updated existing game : {existing.title} | genres : {[g.name for g in existing.genres]}")

        session.commit()

        return existing

    game = Game(
            title = raw.title,
            source_name = raw.source_name,
            source_id = raw.source_id,
            description = raw.description,
            cover_image_url = raw.cover_image_url,
            release_year = raw.release_year
        )

    game.genres = [ get_or_create_genre(session, name) for name in raw.genres ]

    session.add(game)
    session.commit()
    logger.info(f"Saved new game : {game.title}")
    return game