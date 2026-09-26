from os import name
from sqlalchemy.orm import Session

from core.models import Game, Genre, Tag
from sources.base_source import RawGameData
from utils.logger import get_logger
from core.embedding_service import compute_embedding

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

def get_or_create_tag(session : Session, tag_name : str) -> Tag:
    '''
    Looks up Tag by name, creating it if it doesn't exist yet
    '''
    tag = session.query(Tag).filter_by(name = tag_name).first()
    if tag is None:
        tag = Tag(name = tag_name)
        session.add(tag)

    return tag

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

        existing.description_embedding = compute_embedding(raw.description or "")

        existing.genres = [ get_or_create_genre(session, name) for name in raw.genres ]
        existing.tags = [ get_or_create_tag(session, name) for name in raw.tags ]
        logger.info(f"Updated existing game : [ Name : {existing.title}: \n Genres : {[g.name for g in existing.genres]} \n Tags: { [t.name for t in existing.tags] } ]")

        session.commit()

        return existing

    game = Game(
            title = raw.title,
            source_name = raw.source_name,
            source_id = raw.source_id,
            description = raw.description,
            cover_image_url = raw.cover_image_url,
            release_year = raw.release_year,
            description_embedding = compute_embedding(raw.description or "")
        )

    session.add(game)

    game.genres = [ get_or_create_genre(session, name) for name in raw.genres ]
    game.tags = [ get_or_create_tag(session, name) for name in raw.tags ]

    session.commit()
    logger.info(f"Saved new game :\n [Name : {game.title} \n Genres : {[g.name for g in game.genres]} \n Tags : {[t.name for t in game.tags]} ]")
    return game