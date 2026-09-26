from sqlalchemy.orm import Session

from config.settings import Settings
from core.models import Game, QueuedGame, SwipeRecord, User
from core.game_repository import save_game
from sources.registry import SourceRegistry
from core.recommendation_service import RecommendationService
from utils.logger import get_logger

logger = get_logger(__name__)

#Fetch a fresh batch when below this threshold
REFILL_THRESHOLD = 5
#Batches to fetch per refill
FETCH_BATCH_SIZE = 15

class GameQueueService:
    '''
    -Manages user's swipe queue [ordering games]
    -auto refill from sources below threshold
    -decides next game for SwipeView
    '''

    def __init__(self, session : Session, user : User, settings : Settings):
        self.session = session
        self.user = user
        self.registry = SourceRegistry(settings)

    def get_next_game(self) -> Game | None:
        '''
        Returns the next game in the queue
        -None if no games available
        '''

        next_entry = (
                self.session.query(QueuedGame)
                .filter_by(user_id = self.user.id)
                .order_by(QueuedGame.queue_position)
                .first()
            )

        if next_entry is None:
            return None

        game = next_entry.game
        self.session.delete(next_entry)
        self.session.commit()
        return game

    def needs_refill(self) -> bool:
        '''
        checks if queue needs refill (< threshold)
        '''
        remaining_count = (
                self.session.query(QueuedGame)
                .filter_by(user_id = self.user.id)
                .count()
            )
        return remaining_count < REFILL_THRESHOLD

    def refill(self) -> None:
        '''
        Fetches a fresh batch of games
        -adds new games at the end of the queue
        '''

        logger.info(f"refilling game queue")

        already_swiped = {
                s.game_id
                for s in
                self.session.query(SwipeRecord).filter_by(user_id = self.user.id).all()
            }

        already_queued = {
                q.game_id 
                for q in
                self.session.query(QueuedGame).filter_by(user_id = self.user.id).all()
            }

        newly_available_games = []

        for source in self.registry.get_active_sources():
            already_fetched_count = (
                    self.session.query(Game)
                    .filter_by(source_name = source.get_source_name())
                    .count()
                )

            raws = source.fetch_games(limit = FETCH_BATCH_SIZE, offset = already_fetched_count)

            for raw in raws:
                game = save_game(self.session, raw)

                if game.id in already_swiped or game.id in already_queued:
                    continue

                newly_available_games.append(game)
                already_queued.add(game.id)

        recommendor = RecommendationService(self.session, self.user)
        ranked_games = [
                game for game, _ in recommendor.get_top_recommendations(
                        newly_available_games, top_n = len(newly_available_games)
                    )
            ]

        next_position = self.get_next_queue_pos()
        for game in ranked_games:
            queued = QueuedGame(
                    game_id = game.id,
                    user_id = self.user.id,
                    queue_position = next_position
                )
            self.session.add(queued)
            next_position += 1

        self.session.commit()

    def get_next_queue_pos(self) -> int:
        '''
        Finds next queue position available
        '''
        max_pos_entry = (
                self.session.query(QueuedGame)
                .filter_by(user_id = self.user.id)
                .order_by(QueuedGame.queue_position.desc())
                .first()
            )

        return (max_pos_entry.queue_position + 1) if max_pos_entry else 0