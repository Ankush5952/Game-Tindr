from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class OnboardingDialog(QDialog):
    '''
    A one-time window on first-launch
    '''

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Game Tindr")
        self.setFixedSize(420, 260)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Welcome to Game Tindr!")
        title.setStyleSheet("font-size : 20px; font-weight : bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        explaination = QLabel(
                "Swipe Right for interested and left on "
                "uninterested games. \n Your swipes teach Game Tindr your interests "
                "so it can recommend better games over time.\n\n"
                "New games load automatically as you go - just keep swiping!!"
            )
        explaination.setWordWrap(True)
        explaination.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(explaination)

        start_button = QPushButton("Start Swiping")
        start_button.clicked.connect(self.accept)
        layout.addWidget(start_button, alignment= Qt.AlignmentFlag.AlignCenter)

