from collections import defaultdict
from sqlalchemy.orm import Session
import numpy as np

from core.embedding_service import cosine_similarity
from core.models import Game, SwipeRecord, User

class RecommendorService:
    '''
    Computes a simple content-based recommendation score for games based on history{genre preference scores}
    -v1[ heuristic, not ML ]
    '''

    def __init__(self, session : Session, user : User):
        self.session = session
        self.user = user
        self.swipes = (
                self.session.query(SwipeRecord)
                .filter_by(user_id = self.user.id)
                .all()
        )
        self.genre_weights : dict[str, float] = self.compute_label_weights(lambda game : game.genres)
        self.tag_weights : dict[str, float] = self.compute_label_weights(lambda game : game.tags)

        self.liked_embedding_avg = self.compute_liked_embedding_average()

    def compute_label_weights(self, get_labels) -> dict[str, float]:
        '''
        Returns a { <label_name> : <label_weight> } dict
        - weights normalized to [-1, 1] interval
        - unswiped label score = 0
        '''

        liked_counts = defaultdict(int)
        disliked_counts = defaultdict(int)

        for swipe in self.swipes:
            for label in get_labels(swipe.game):
                if swipe.liked:
                    liked_counts[label.name] += 1
                else:
                    disliked_counts[label.name] += 1

        all_label_names = set(liked_counts) | set(disliked_counts)
        weights = {}
        for name in all_label_names:
            liked = liked_counts[name]
            disliked = disliked_counts[name]

            total = liked + disliked
            weights[name] = (liked - disliked) / total

        return weights

    def compute_liked_embedding_average(self) -> bytes:
        '''
        Averages th description embeddings of every liked game into a single 
        'taste vector'.
        -returns empty bytes if no liked embedding data
        '''

        liked_embeddings = [
                np.frombuffer(swipe.game.description_embedding, dtype=np.float32)
                for swipe in self.swipes
                if swipe.liked and swipe.game.description_embedding
            ]

        if not liked_embeddings:
            return b""

        avg_vector = np.mean(liked_embeddings, axis=0)
        return avg_vector.astype(np.float32).tobytes()

    def score_game(self, game : Game) -> float:
        '''
        Returns a recommendation score for a single game
        based on genre, tag and description scores
        '''
        genre_w = [self.genre_weights.get(g.name, 0.0) for g in game.genres]
        genre_score = sum(genre_w)/len(genre_w)
        
        tag_w = [self.tag_weights.get(t.name, 0.0) for t in game.tags]
        tag_score = sum( tag_w )/len(tag_w)

        description_score = cosine_similarity(
                self.liked_embedding_avg, game.description_embedding or b""
            )
        
        return genre_score + tag_score + description_score

    def get_top_recommendations(self, games : list[Game], top_n : int = 5) -> list[tuple[Game, float]]:
        '''
        Scores a list of candidate games and returns a top_n highest
        '''

        scored = [ ( game, self.score_game(game) ) for game in games ]
        scored.sort(key = lambda pair : pair[1], reverse = True)
        return scored[:top_n]

