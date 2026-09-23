from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QCheckBox, QApplication

from config.settings import Settings
from ui.theme_loader import load_stylesheet
from utils.logger import get_logger

logger = get_logger(__name__)

KNOWN_SOURCES = {
       "igdb" : "IGDB"
    }

class SettingsView(QWidget):
    '''
    Settings screen
    -live change apply
    '''

    def __init__(self, settings : Settings):
        super().__init__()
        self.settings = settings

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.build_theme_section())
        layout.addWidget(self.build_sources_section())
        layout.addStretch() #oushes content to top instead of vertically center

    def build_theme_section(self) -> QWidget:
        section = QWidget()
        section_layout = QVBoxLayout()
        section.setLayout(section_layout)

        heading = QLabel("Theme")
        heading.setStyleSheet("font-size : 16px; font-weight : bold;")
        section_layout.addWidget(heading)

        theme_dropdown = QComboBox()
        theme_dropdown.addItems(["dark", "light"])
        theme_dropdown.setCurrentText(self.settings.active_theme)
        theme_dropdown.currentTextChanged.connect(self.on_theme_changed)
        section_layout.addWidget(theme_dropdown)

        return section

    def on_theme_changed(self, theme_name : str) -> None:
        self.settings.set_active_theme(theme_name)

        app = QApplication.instance()
        app.setStyleSheet(load_stylesheet(theme_name))

        logger.info(f"Theme changed to '{theme_name}'")

    def build_sources_section(self) -> QWidgets:
        section = QWidget()
        section_layout = QVBoxLayout()
        section.setLayout(section_layout)

        heading = QLabel("Data Sources")
        heading.setStyleSheet("font-size : 16px; font-weight : bold;")
        section_layout.addWidget(heading)

        for key, name in KNOWN_SOURCES.items():
            checkbox = QCheckBox(name)
            is_enabled = self.settings.enabled_sources.get(key, False)
            checkbox.setChecked(is_enabled)

            checkbox.toggled.connect(
                    lambda checked, key = key : self.on_source_toggled(key, checked)
                )

            section_layout.addWidget(checkbox)

        return section

    def on_source_toggled(self, source_key : str, enabled : bool) -> None:
        self.settings.set_source_enabled(source_key, enabled)
        logger.info(f"Source '{source_key}' {'enabled' if enabled else 'disabled'}")
