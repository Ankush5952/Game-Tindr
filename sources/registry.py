from config.settings import Settings
from sources.base_source import GameDataSource
from sources.igdb_source import IGDBSource
from sources.rawg_source import RAWGSource
from utils.logger import get_logger

logger = get_logger(__name__)

class SourceRegistry:
    '''
    Knows every GameDataSource that exists and enabled
    Used by the app to call sources wihtout importing them directly
    '''

    def __init__(self, settings : Settings):
        self._settings = settings

        self._factories = {
                "igdb" : lambda: IGDBSource(settings),
                "rawg" : lambda : RAWGSource(settings),
                #"steam" : lamba : SteamSource(settings),
            }

    def get_active_sources(self) -> list[GameDataSource]:
        '''
        Returns instances of every source that is known and enabled
        '''

        active = []
        for source_key, is_enabled in self._settings.enabled_sources.items():
            if not is_enabled:
                continue;
            factory = self._factories.get(source_key)
            if factory is None:
                logger.warning(
                        f"Config enables unknown source '{source_key}' - ignoring"
                    )
                continue
            active.append(factory())

        if not active:
            logger.warning("No active data sources configured")

        return active

