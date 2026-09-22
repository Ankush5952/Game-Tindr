from PySide6.QtCore import QThread, Signal

from config.settings import Settings
from core.database import get_session
from core.models import User
from core.game_queue_service import GameQueueService
from utils.logger import get_logger

logger = get_logger(__name__)

class QueueRefillWorker(QThread):
    '''
    Runs a seperate background thread for refill queue service
    -prevents freezing UI due to fetch operations
    '''

    finished_refill = Signal()

    def run(self) -> None:
        '''
        Called automatically by Qt when .start() is invoked
        -runs on bg thread
        '''
        session = get_session()
        try:
            user = session.query(User).first()
            settings = Settings.load()
            queue_service = GameQueueService(session, user, settings)
            queue_service.refill()
        except Exception:
            logger.exception("Background queue refill failed")
        finally:
            session.close()

        self.finished_refill.emit()