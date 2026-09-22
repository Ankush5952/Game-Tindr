from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel

from core.database import get_session
from core.models import Game
from ui.swipe_card_widget import GameCardWidget

class MainWindow(QWidget):
    '''
    App's main window
    - holds tab nav
    '''

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Tindr")
        self.resize(800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self.build_swipe_tab(), "Swipe")
        self.tabs.addTab(self.build_placeholder("Profile screen - Phase 7"), "Profile")
        self.tabs.addTab(self.build_placeholder("Settings screen - Phase 6"), "Settings")


    def build_swipe_tab(self) -> QWidget:
        '''
        Builds the Swipe tab
        '''
        page = QWidget()
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)

        session = get_session()

        game = session.query(Game).first()

        if game is None:
            page_layout.addWidget(QLabel("No games in db"))
        else:
            page_layout.addWidget(GameCardWidget(game))

        session.close()

        return page

    def build_placeholder(self, text:str) -> QWidget:
        '''
        Builds a simple placeholder page with text
        '''
        page = QWidget()
        page_layout =QVBoxLayout()
        page.setLayout(page_layout)

        label = QLabel(text)
        page_layout.addWidget(label)

        return page
