import time

from config.settings import Settings
from sources.base_source import GameDataSource, RawGameData
from utils.http_client import post_json, post_text, HttpClientError
from utils.logger import get_logger

logger = get_logger(__name__)

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
IGDB_GAMES_URL = "https://api.igdb.com/v4/games"

class IGDBSource(GameDataSource):
    '''
    Fetches games from IGDB
    Requires Twitch Developer Client ID/Secret from .env
    '''

    def __init__(self, settings : Settings):
        self._client_id = settings.igdb_client_id
        self._client_secret = settings.igdb_client_secret
        self._access_token : str | None = None
        self._token_expires_at : float = 0.0

        if not self._client_id or not self._client_secret:
            logger.warning(
                "IGDB credentials missing - set IGDB_CLIENT_ID and IGDB_CLIENT_SECRET in your .env file"
                )

    def get_source_name(self) -> str:
        return "igdb"

    def _get_access_token(self) -> str:
        '''
        Returns a valid access token, fetching a new one if the old one expires
        '''
        if self._access_token and time.time() < self._token_expires_at():
            return self._access_token

        logger.info("Reqiesting new IGDB access token")
        response = post_json(
                TWITCH_TOKEN_URL,
                data = {
                    "client_id" : self._client_id,
                    "client_secret" : self._client_secret,
                    "grant_type" : "client_credentials"
                    }
            )

        self._access_token = response["access_token"]
        self._token_expires_at = time.time() + response["expires_in"] - 60 #subtracting 60s as buffer time

        return self._access_token

    def fetch_games(self, limit : int = 30) -> list[RawGameData]:
        '''
        Fetches 'limit' popular games from IGDB and converts them into RawGameData
        '''

        token = self._get_access_token()

        headers = {
            "Client-ID" : self._client_id,
            "Authorization" : f"Bearer {token}"
            }

        #Apicalypse query
        query = (
                "fields name,summary,first_release_date,cover.url,"
                "genres.name,tags,keywords.name;"
                f"sort total_rating_count desc;"
                f"limit {limit};"
            )

        try:
            raw_games = post_text(IGDB_GAMES_URL, body = query, headers =headers)
        except HttpClientError:
            logger.error("Failed to fetch games from IGDB")
            return []

        results = []
        for raw in raw_games:
            results.append(self._to_raw_game_data(raw))

        logger.info(f"Fetched {len(results)} games from IGDB")
        return results

    def _to_raw_game_data(self, raw : dict) -> RawGameData:
        '''
        Converts IGDB's raw JSON to generic RawGameData
        '''

        cover_url = None
        if "cover" in raw and "url" in raw["cover"]:
            cover_url = "https:" + raw["cover"]["url"].replace("t_thumb", "t_cover_big")

        release_year = None
        if "first_release_date" in raw:
            release_year = time.gmtime( raw["first_release_date"] ).tm_year

        genres = [ g["name"] for g in raw.get("genres", []) ]

        return RawGameData(
                source_name=self.get_source_name(),
                source_id=str(raw["id"]),
                title=raw.get("name", "Unknown"),
                description=raw.get("summary"),
                cover_image_url=cover_url,
                release_year=release_year,
                genres=genres,
                tags=[] #Will revisit this
            )