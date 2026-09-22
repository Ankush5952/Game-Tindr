from abc import ABC, abstractclassmethod
from dataclasses import dataclass, field
from tarfile import DEFAULT_FORMAT

@dataclass
class RawGameData:
    '''
    A generic representation of a game as fetched from any source
    Every source must translate their format -> this shape from their API
    '''

    source_name : str
    source_id : int
    title : str
    description : str | None = None
    cover_image_url : str | None = None
    release_year : int | None = None
    genres : list[str] = field(default_factory=list)
    tags : list[str] = field(default_factory=list)

class GameDataSource(ABC):
    '''
    Abstract contract every source must follow
    Rest of the app only depends on this interface instead of any source
    '''

    @abstractclassmethod
    def get_source_name(self) -> str:
        '''
        Returns a short unique indentifier for the source
        '''
        raise NotImplementedError

    @abstractclassmethod
    def fetch_games(self, limit : int = 20) -> list[RawGameData]:
        '''
        Fetches upto limit games from this source and returns them as a RawGameData list
        '''
        raise NotImplementedError