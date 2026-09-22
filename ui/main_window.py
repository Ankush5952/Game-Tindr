from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel

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

        self.tabs.addTab(self.build_placeholder("Swipe screen - Phase 4"), "Swipe")
        self.tabs.addTab(self.build_placeholder("Profile screen - Phase 7"), "Profile")
        self.tabs.addTab(self.build_placeholder("Settings screen - Phase 6"), "Settings")

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
