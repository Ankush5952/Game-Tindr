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
        self.swipes = (
                self.session.query(SwipeRecord)
                .filter_by(user_id = self.user.id)
                .all()
        )
        self.genre_weights : dict[str, float] = self.compute_genre_weights(lambda game : game.genres)
        self.tag_weights : dict[str, float] = self.compute_genre_weights(lambda game : game.tags)

    def compute_genre_weights(self, get_labels) -> dict[str, float]:
        '''
        Returns a { <genre_name> : <genre_weight> } dict
        - weights normalized to [-1, 1] interval
        - unswiped genre score = 0
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

    def score_game(self, game : Game) -> float:
        '''
        Returns a recommendation score for a single game
        '''
        genre_score = sum( self.genre_weights.get(g.name, 0.0) for g in game.genres )
        tag_score = sum( self.tag_weights.get(t.name, 0.0) for t in game.tags )
        
        return genre_score + tag_score

    def get_top_recommendations(self, games : list[Game], top_n : int = 5) -> list[tuple[Game, float]]:
        '''
        Scores a list of candidate games and returns a top_n highest
        '''

        scored = [ ( game, self.score_game(game) ) for game in games ]
        scored.sort(key = lambda pair : pair[1], reverse = True)
        return scored[:top_n]

