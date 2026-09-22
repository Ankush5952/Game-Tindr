from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from core.models import Game
from utils.http_client import get_bytes, HttpClientError
from utils.logger import get_logger

logger = get_logger(__name__)

class GameCardWidget(QWidget):
    '''
    Displays cover image, title and genres
    '''

    def __init__(self, game:Game):
        super().__init__()
        self.game = game

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setFixedSize(300, 400)
        layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.load_cover_image()

        self.title_label =QLabel(game.title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size : 18px; font-weight : bold;")
        layout.addWidget(self.title_label)

        genre_names = ",".join(genre.name for genre in game.genres)
        self.genre_label = QLabel(genre_names, alignment=Qt.AlignmentFlag.AlignCenter)
        self.genre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.genre_label)

    
    def load_cover_image(self) -> None:
        '''
        Downloads and displays game's cover image
        '''
        if not self.game.cover_image_url:
            self.cover_label.setText("No cover available")
            return

        try:
            image_bytes = get_bytes(self.game.cover_image_url)
        except HttpClientError:
            logger.warning(f"Could not load cover for {self.game.title}")
            self.cover_label.setText(f"Failed to load cover")
            return

        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)

        scaled = pixmap.scaled(
                300, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        self.cover_label.setPixmap(scaled)