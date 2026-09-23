from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel

from ui.swipe_view import SwipeView
from ui.settings_view import SettingsView
from ui.profile_view import ProfileView
from config.settings import Settings

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
        
        settings = Settings.load()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.profile_view = ProfileView(settings.active_theme)
        self.settings_view = SettingsView(settings)

        self.settings_view.theme_changed.connect(self.profile_view.set_theme)

        self.tabs.addTab(SwipeView(), "Swipe")
        self.tabs.addTab(self.profile_view, "Profile")
        self.tabs.addTab(self.settings_view, "Settings")

        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index : int) -> None:
        if self.tabs.widget(index) is self.profile_view:
            self.profile_view.refresh()


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
