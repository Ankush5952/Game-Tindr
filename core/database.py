from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.models import Base

DB_PATH = Path(__file__).resolve().parent.parent/"game_tindr.db"

#Engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo = False)

#Session factory - SessionLocal()
SessionLocal = sessionmaker(bind = engine)

def init_db() -> None:
    '''
    Creates all tables if they don't exist
    Safe to call - no data wipe risk
    '''
    Base.metadata.create_all(bind = engine)

def get_session() -> Session:
    '''
    Returns a new database session
    '''
    return SessionLocal()
