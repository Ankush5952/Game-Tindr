from collections import Counter
from sqlalchemy.orm import Session

from core.models import SwipeRecord, User

def get_genre_breakdown(session : Session, user : User, liked : bool) -> dict[str, float]:
    '''
    Computes like-dslike genre percentage
    '''

    swipes = (
            session.query(SwipeRecord)
            .filter_by(user_id = user.id, liked = liked)
            .all()
        )

    if not swipes:
        return {}

    genre_counts = Counter()
    for swipe in swipes:
        for genre in swipe.game.genres:
            genre_counts[genre.name] += 1

    total_genre_mentions = sum(genre_counts.values())
    if total_genre_mentions == 0:
        return {}

    return {
            genre_name : round( (count/total_genre_mentions) * 100, 1 )
            for genre_name, count in  genre_counts.items()
        }
