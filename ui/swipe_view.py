from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt

from core.database import get_session
from core.models import Game, SwipeRecord, User
from ui.swipe_card_widget import GameCardWidget
from utils.logger import get_logger

logger = get_logger(__name__)

class SwipeView(QWidget):
    '''
    Manages the swipe screen 
    - shows one game card at a time
    - records each swipe to db
    - loads next game card
    '''

    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 550)

        self.current_card : GameCardWidget | None = None
        self.no_games_label : QLabel | None = None

        self.load_next_card()

    def load_next_card(self) -> None:
        '''
        Fetches next not-yet swiped game and displays it as a card
        '''
        session = get_session()

        try:
            user = session.query(User).first()

            #Find a game this user hasn't swiped yet
            already_swiped_ids = [
                    swipe.game_id
                    for swipe in 
                    session.query(SwipeRecord).filter_by(user_id = user.id).all()
                ]

            game = (
                    session.query(Game)
                    .filter(~Game.id.in_(already_swiped_ids))
                    .first()
                )

            if game is None:
                self.show_no_games_message()
                return

            card = GameCardWidget(game)
            card.setParent(self)
            card.move(250, 30)
            card.swiped.connect(lambda liked : self.on_swiped(game.id, liked))
            card.show()

            self.current_card = card
        finally:
            session.close()

    def on_swiped(self, game_id : int, liked : bool) -> None:
        '''
        Called when swipe anim finishes
        -records the swipe
        -removes old card
        -loads next card
        '''

        session = get_session()

        try:
            user = session.query(User).first()
            swipe = SwipeRecord(
                user_id = user.id,
                game_id = game_id,
                liked = liked
                )
            session.add(swipe)
            session.commit()
            logger.info(f"Recorded swipe : game_id ={game_id} liked = {liked}")
        finally:
            session.close()

        if self.current_card is None:
            self.current_card.deleteLater()
            self.current_card = None

        self.load_next_card()

    def show_no_games_message(self) -> None:
        label = QLabel("No more games to swipe")
        label.setParent(self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 200, 800, 50)
        label.show()
        self.no_games_label = label