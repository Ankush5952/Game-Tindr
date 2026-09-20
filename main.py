import sys
from PySide6.QtWidgets import QApplication, QWidget

#Manages whole GUI app - handles event loop
app = QApplication(sys.argv)

#base class for anything visual
window = QWidget()
window.setWindowTitle("Game Tindr - Phase 0")
window.resize(400, 300)
window.show()

#closes the app with the right exit code
sys.exit(app.exec())