from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QPoint, QEasingCurve

from core.models import Game
from utils.http_client import get_bytes, HttpClientError
from utils.logger import get_logger

logger = get_logger(__name__)

SWIPE_THRESHOLD = 100

class GameCardWidget(QWidget):
    '''
    Displays cover image, title and genres
    '''

    #emitted when a swipe completes : True(right), False(left)
    swiped = Signal(bool)

    def __init__(self, game:Game):
        super().__init__()
        self.game = game

        self.drag_start_mouse_pos : QPoint | None = None
        self.drag_start_widget_pos : QPoint | None = None

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

        genre_names = "Genres : " + ",".join(genre.name for genre in game.genres)
        self.genre_label = QLabel(genre_names, alignment=Qt.AlignmentFlag.AlignCenter)
        self.genre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.genre_label)

        self.setFixedSize(340, 480)

    
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

#----DRAG HANDLING -----
    def mousePressEvent(self, event : QMouseEvent) -> None:
        '''
        Called automatically by Qt when user presses mouse button on this widget
        '''
        if(event.button() == Qt.MouseButton.LeftButton) :
            self.drag_start_mouse_pos = event.globalPosition().toPoint()
            self.drag_start_widget_pos = self.pos()

    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        '''
        Called continously while mouse movement while button held down
        '''

        if self.drag_start_mouse_pos is None:
            return

        current_pos = event.globalPosition().toPoint()
        delta = current_pos - self.drag_start_mouse_pos

        new_x =self.drag_start_widget_pos.x() + delta.x()
        new_y = self.drag_start_widget_pos.y()
        self.move(new_x, new_y)

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        '''
        Called when mouse button is released
        '''
        if self.drag_start_widget_pos is None:
            return

        horizontal_dist = self.pos().x() - self.drag_start_widget_pos.x()

        if horizontal_dist > SWIPE_THRESHOLD:
            self.animate_off_screen(direction = 1)
        elif horizontal_dist < -SWIPE_THRESHOLD:
            self.animate_off_screen(direction = -1)
        else:
            self.snap_back()

        self.drag_start_mouse_pos = None
        self.drag_start_widget_pos = None

    def snap_back(self) -> None:
        '''
        Animates the card back to its starting position
        '''
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.drag_start_widget_pos)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def animate_off_screen(self, direction : int) -> None:
        '''
        Animated the card to either side of the screen(1 for right, -1 for left)
        emits a signal after animation end
        '''

        end_x = self.pos().x() + direction*600
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(end_x, self.pos().y()))
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)

        liked = direction > 0
        self.animation.finished.connect(lambda: self.swiped.emit(liked))
        self.animation.start()

