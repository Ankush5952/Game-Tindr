from datetime import UTC, datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean, Table, Column, LargeBinary
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    '''
    Base Class every model inherits from
    '''
    pass

#----Association Tables----
game_genre_association = Table(
    "game_genre",
    Base.metadata,
    Column("game_id", ForeignKey("games.id"), primary_key = True),
    Column("genre_id", ForeignKey("genres.id"), primary_key = True)
)

game_tag_association = Table(
        "game_tag",
        Base.metadata,
        Column("game_id", ForeignKey("games.id"), primary_key=True),
        Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)

#----Classes----
class Genre(Base):
    '''
    Game genre
    '''
    __tablename__ = "genres"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(100), unique=True)

    games : Mapped[list["Game"]] = relationship(
            secondary=game_genre_association, back_populates="genres"
        )

    def repr(self) -> str:
        return f"<Genre {self.name}"

class Tag(Base):
    '''
    Game tag
    '''
    __tablename__ = "tags"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(100), unique = True)

    games : Mapped[list["Game"]] = relationship(
            secondary=game_tag_association, back_populates="tags"
        )

    def repr(self) -> str:
        return f"<Tag {self.name}"

class Game(Base):
    '''
    Game
    '''
    __tablename__ = "games"

    id : Mapped[int] = mapped_column(primary_key = True)
    title : Mapped[str] = mapped_column(String(255))

    source_name : Mapped[str] = mapped_column(String(50))
    source_id : Mapped[str] = mapped_column(String(100))

    description : Mapped[str | None] = mapped_column(String(2000), nullable=True)
    description_embedding : Mapped[LargeBinary | None] = mapped_column(LargeBinary, nullable=True)
    cover_image_url : Mapped[str | None] = mapped_column(String(500), nullable=True)
    release_year : Mapped[int | None] = mapped_column(Integer, nullable=True)

    genres : Mapped[list["Genre"]] = relationship(
            secondary=game_genre_association, back_populates="games"
        )
    tags : Mapped[list["Tag"]] = relationship(
            secondary=game_tag_association, back_populates="games"
        )

    def repr(self) -> str:
        return f"<Game {self.title}"

class User(Base):
    '''
    user of this app
    -currently local only
    '''
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    display_name : Mapped[str] = mapped_column(String(100), default = "Player")
    created_at : Mapped[datetime] = mapped_column(
            DateTime, default = lambda : datetime.now(UTC)
        )

    swipes : Mapped[list["SwipeRecord"]] = relationship(back_populates = "user")

    def repr(self) -> str:
        return f"User {self.display_name}"

class SwipeRecord(Base):
    '''
    swipe action record per user
    '''
    __tablename__ = "swipe_records"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    game_id : Mapped[int] = mapped_column(ForeignKey("games.id"))

    #True = right swipe, False = left swipe
    liked : Mapped[bool] = mapped_column(Boolean)
    swiped_at : Mapped[datetime] = mapped_column(
            DateTime, default = lambda: datetime.now(UTC)
        )

    user : Mapped["User"] = relationship(back_populates="swipes")
    game : Mapped["Game"] = relationship()

    def repr(self) -> str:
        direction = "RIGHT" if self.liked else "LEFT"
        return f"<Swipe {direction} on game_id={self.game_id}"

class QueuedGame(Base):
    '''
    Tracks games shown but not swiped for inter-session persistance
    '''
    __tablename__ = "queued_games"

    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    game_id : Mapped[int] = mapped_column(ForeignKey("games.id"))

    #Order in queue
    queue_position : Mapped[int] = mapped_column(Integer)

    user : Mapped["User"] = relationship()
    game : Mapped["Game"] = relationship()

    def repr(self) -> str:
        return f"<QueuedGame game_id = {self.game_id} position = {self.queue_position}"

