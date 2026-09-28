from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt

from core.database import get_session
from core.models import SwipeRecord, User
from ui.swipe_card_widget import GameCardWidget
from core.game_queue_service import GameQueueService
from ui.queue_refill_worker import QueueRefillWorker
from utils.logger import get_logger
from config.settings import Settings

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
        self.setFixedSize(800, 1080)

        self.current_card : GameCardWidget | None = None
        self.no_games_label : QLabel | None = None
        self.refill_worker : QueueRefillWorker | None = None

        self.load_next_card()

    def load_next_card(self) -> None:
        '''
        Fetches next not-yet swiped game and displays it as a card
        '''
        session = get_session()

        try:
            user = session.query(User).first()

            settings = Settings.load()
            queue_service = GameQueueService(session, user, settings)

            game = queue_service.get_next_game()
            needs_refill = queue_service.needs_refill()
            
            card = GameCardWidget(game) if game is not None else None
        finally:
            session.close()

        if needs_refill:
            self.trigger_background_refill()

        self.clear_no_games_label()
            
        if game is None:
            self.show_no_games_message()
            return

        card.setParent(self)
        card_x = (self.width() - card.width())//2
        card_y = (self.height() - card.height())//2
        card.move(card_x, -card_y)
        card.swiped.connect(lambda liked, gid=game.id : self.on_swiped(gid, liked))
        card.show()

        self.current_card = card

    def trigger_background_refill(self) -> None:
        '''
        Starts a bg refill, unless one is alr running
        '''
        if self.refill_worker is not None and self.refill_worker.isRunning():
            return

        logger.info("Queue running low - starting bg refill")
        self.refill_worker = QueueRefillWorker()
        self.refill_worker.finished_refill.connect(self.on_refill_finished)
        self.refill_worker.start()

    def on_refill_finished(self) -> None:
        '''
        Post refill event trigger function
        '''
        logger.info("Bg refill finished")
        if self.current_card is None:
            self.load_next_card()

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

            queue_service = GameQueueService(session, user, Settings.load())
            queue_service.remove_from_queue(game_id)
        finally:
            session.close()

        if self.current_card is not None:
            self.current_card.deleteLater()
            self.current_card = None

        self.load_next_card()

    def show_no_games_message(self) -> None:
        label = QLabel("Loadig...")
        label.setParent(self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 200, 800, 50)
        label.show()
        self.no_games_label = label

    def clear_no_games_label(self) -> None:
        if self.no_games_label is not None:
            self.no_games_label.deleteLater()
            self.no_games_label = None