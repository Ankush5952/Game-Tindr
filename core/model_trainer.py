import pickle
from pyexpat import features

import numpy as np
from scipy.stats import cosine
from sklearn.linear_model import LogisticRegression
from sqlalchemy.orm import Session

from core.models import Game, SwipeRecord, User
from core.embedding_service import cosine_similarity
from utils.logger import get_logger
from utils.paths import get_app_data_path

logger = get_logger(__name__)

MODEL_PATH = get_app_data_path()/"recommendor_model.pkl"

MIN_SWIPES_TO_TRAIN = 15

class TrainedRecommendor:
    '''
    A trained scikit-learn model for like/dislike prediction
    '''

    def __init__(self, session : Session, user : User):
        self.session = session
        self.user = user
        self.model : LogisticRegression | None = None
        self.genre_weights : dict[str, float] = {}
        self.tag_weights : dict[str, float] = {}
        self.description_avg : bytes = b"" #Liked embedding average

    def can_train(self) -> bool:
        '''
        Checks if there;s enough data to train
        '''
        swipe_count = (
                self.session.query(SwipeRecord)
                .filter_by(user_id = self.user.id)
                .count()
            )

        return swipe_count >= MIN_SWIPES_TO_TRAIN

    def train(self) -> None:
        '''
        Fits a LR model on user's swipe history
        -recomputes genre and tag weights; and description score
        '''

        swipes = (
                self.session.query(SwipeRecord)
                .filter_by(user_id = self.user.id)
                .all()
            )

        self.genre_weights = self.build_label_weights(swipes, lambda g : g.genres)
        self.tag_weights = self.build_label_weights(swipes, lambda t : t.tags)
        self.description_avg = self.compute_description_avg(swipes)

        features = []
        labels = []

        for swipe in swipes:
            features.append(self.build_feature_vector(swipe.game))
            labels.append(int(swipe.liked))

        self.model = LogisticRegression()
        self.model.fit(np.array(features), np.array(labels))

        logger.info(
                f"Trained recommendor model on {len(swipes)} swipes. "
                f"Learned coeffecieny=ts : [Genre = {self.model.coef_[0][0]:.3f}], "
                f"[Tag = {self.model.coef_[0][1]:.3f}], "
                f"[Description = {self.model.coef_[0][2]:.3f}]\n"
            )
        self.save()

    def predict_score(self, game : Game) -> float:
        '''
        Returns model's predicted score of the game for the user
        -requires train() to have been called first
        '''

        if self.model is None:
            raise RuntimeError(f"Model is not trained yet - call train() first")

        features = np.array( [ self.build_feature_vector(game) ] )

        #predicted returns [prob_0, prob_1] - we want prob of 1(liked)
        return float(self.model.predict_proba(features)[0][1])

    def build_feature_vector(self, game : Game) -> list[float]:
        '''
        Convertsa game into a 3-feature vector
        - game genre avg
        - game tag avg
        - game desc score
        '''

        genre_weights = [ self.genre_weights.get(g.name, 0.0) for g in game.genres ]
        genre_score = sum(genre_weights) / len(genre_weights) if genre_weights else 0.0

        tag_weights = [ self.tag_weights.get(g.name, 0.0) for g in game.tags ]
        tag_score = sum(tag_weights) / len(tag_weights) if tag_weights else 0.0

        description_score = cosine_similarity(
                self.description_avg, game.description_embedding or b""
            )

        return [genre_score, tag_score, description_score]

    def build_label_weights(self, swipes : SwipeRecord, get_labels) -> dict[str, float]:
        from collections import defaultdict

        liked_counts = defaultdict(int)
        disliked_counts = defaultdict(int)

        for swipe in swipes:
            for label in get_labels(swipe.game):
                if swipe.liked:
                    liked_counts[label.name] += 1
                else:
                    disliked_counts[label.name] += 1

        all_names = set(liked_counts) | set(disliked_counts)

        return {
                name : ( liked_counts[name] - disliked_counts[name] ) / ( liked_counts[name] + disliked_counts[name] )
                for name in all_names
            }

    def compute_description_avg(self, swipes : SwipeRecord) -> bytes:
        liked_embeddings = [
                np.frombuffer(swipe.game.description_embedding, dtype = np.float32)
                for swipe in swipes
                if swipe.liked and swipe.game.description_embedding
            ]
        if not liked_embeddings:
            return b""

        return np.mean(liked_embeddings, axis = 0).astype(np.float32).tobytes()

    def save(self) -> None:
        '''
        Persists the trained model and weights to disk
        '''
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump({
                    "model" : self.model,
                    "genre_weights" : self.genre_weights,
                    "tag_weights" : self.tag_weights,
                    "description_avg" : self.description_avg
                }, f)


    def load(self) -> bool :
        '''
        Loads a previously trained model from disk if exists
        -return false otherwise
        '''
        if not MODEL_PATH.exists():
            return False

        with open(MODEL_PATH, 'rb') as f:
            data = pickle.load(f)

        self.model = data["model"]
        self.genre_weights = data["genre_weights"]
        self.tag_weights = data["tag_weights"]
        self.description_avg = data["description_avg"]

        return True
