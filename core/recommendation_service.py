from sys import setswitchinterval
from sqlalchemy.orm import Session

from core.models import Game, User, SwipeRecord
from core.recommendor_service import RecommendorService
from core.model_trainer import TrainedRecommendor
from utils.logger import get_logger

logger = get_logger(__name__)

#Retrain the model with fresh data every N swipes
RETRAIN_EVERY_N_SWIPES = 20

class RecommendationService:
    '''
    Single entry point the rest of the app uses for recommendation scoring.
    -Uses the trained ML model if available, otherwise fallback to heuristic model
    '''

    def __init__(self, session : Session, user : User):
        self.session = session
        self.user = user
        self.heuristic = RecommendorService(session, user)

        self.trained = TrainedRecommendor(session, user)
        self.using_trained_model = self.trained.load()

        self.maybe_retrain()

    def maybe_retrain(self) -> None:
        '''
        Retrains the model if enough swipes have been made since last training
        '''

        swipe_count = (
                self.session.query(SwipeRecord)
                .filter_by(user_id = self.user.id)
                .count()
            )

        if not self.trained.can_train():
            return

        should_retrain = (
                not self.using_trained_model
                or swipe_count % RETRAIN_EVERY_N_SWIPES == 0
            )

        if should_retrain:
            logger.info(f"Retraining recommendor model at {swipe_count} swipes")
            self.trained.train()
            self.using_trained_model = True

    def score_game(self, game : Game, use_ml : bool = True) -> float:
        '''
        Returns a recommendation score for a game
        '''
        if self.using_trained_model and use_ml:
            return self.trained.predict_score(game)

        return self.heuristic.score_game(game)

    def get_top_recommendations(self, games : list[Game], top_n : int = 5, use_ml : bool = True) -> list[tuple[Game, float]]:
        scored = [(game, self.score_game(game, use_ml)) for game in games]
        scored.sort(key = lambda pair : pair[1], reverse=True)
        return scored[:top_n]

    def is_using_trained_model(self) -> bool:
        return self.using_trained_model