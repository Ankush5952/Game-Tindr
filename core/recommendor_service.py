from collections import defaultdict
from sqlalchemy.orm import Session

from core.models import Game, SwipeRecord, User

class RecommendorService:
    '''
    Computes a simple content-based recommendation score for games based on history{genre preference scores}
    -v1[ heuristic, not ML ]
    '''

    def __init__(self, session : Session, user : User):
        self.session = session
        self.user = user
        self.genre_weights : dict[str, float] = self.compute_genre_weights()

    def compute_genre_weights(self) -> dict[str, float]:
        '''
        Returns a { <genre_name> : <genre_weight> } dict
        - weights normalized to [-1, 1] interval
        - unswiped genre score = 0
        '''

        swipes = (
                self.session.query(SwipeRecord)
                .filter_by(user_id = self.user.id)
                .all()
            )

        liked_counts = defaultdict(int)
        disliked_counts = defaultdict(int)

        for swipe in swipes:
            for genre in swipe.game.genres:
                if swipe.liked:
                    liked_counts[genre.name] += 1
                else:
                    disliked_counts[genre.name] += 1

        all_genre_names = set(liked_counts) | set(disliked_counts)
        weights = {}
        for genre_name in all_genre_names:
            liked = liked_counts[genre_name]
            disliked = disliked_counts[genre_name]

            total = liked + disliked
            weights[genre_name] = (liked - disliked) / total

        return weights

    def score_game(self, game : Game) -> float:
        '''
        Returns a recommendation score for a single game
        '''
        return sum(
            self.genre_weights.get(genre.name, 0.0) 
            for genre in game.genres
            )

    def get_top_recommendations(self, games : list[Game], top_n : int = 5) -> list[tuple[Game, float]]:
        '''
        Scores a list of candidate games and returns a top_n highest
        '''

        scored = [ ( game, self.score_game(game) ) for game in games ]
        scored.sort(key = lambda pair : pair[1], reverse = True)
        return scored[:top_n]

