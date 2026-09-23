from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from core.database import get_session
from core.models import User
from core.analytics_service import get_genre_breakdown
from ui.theme_loader import load_palette

class ProfileView(QWidget):
    '''
    Shows the user profile
    -swipe analytics
    '''

    def __init__(self, active_theme : str):
        super().__init__()
        self.active_theme = active_theme
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.refresh()

    def set_theme(self, theme_name : str) -> None:
        '''
        Called when user changes theme
        '''
        self.active_theme = theme_name
        self.refresh()

    def refresh(self) -> None:
        '''
        Clears and rebuilds charts from db
        '''
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        palette = load_palette(self.active_theme)

        session = get_session()
        try:
            user = session.query(User).first()
            liked_breakdown = get_genre_breakdown(session, user, liked=True)
            disliked_breakdown = get_genre_breakdown(session, user, liked =False)
        finally:
            session.close()

        if not liked_breakdown and not disliked_breakdown:
            label = QLabel("Swipe on some games to see analytics")
            label.setStyleSheet(f"color : {palette['text']};")
            self.layout.addWidget(label)
            return

        self.layout.addWidget(
            self.build_chart("Liked Genres", liked_breakdown, palette, bar_color = palette['accent'])
            )
        self.layout.addWidget(
            self.build_chart("Disliked Genres", disliked_breakdown, palette, bar_color = '#ff7875')
            )

    def build_chart(
        self, title : str, breakdown : dict[str, float], palette : dict, bar_color : str
        ) -> FigureCanvasQTAgg:
        '''
        Builds a bar chart
        -horizontal bars
        '''

        figure = Figure(figsize=(6,3))
        figure.patch.set_facecolor(palette['surface'])

        canvas = FigureCanvasQTAgg(figure)
        ax = figure.add_subplot(111)
        ax.set_facecolor(palette['surface'])

        ax.tick_params(colors = palette['text'])
        ax.xaxis.label.set_color(palette['text'])
        ax.title.set_color(palette['text'])
        for spine in ax.spines.values():
            spine.set_color(palette['border'])

        if not breakdown:
            ax.text(0.5, 0.5, "No data yet", ha = "center", va = "center", color = palette['text_secondary'])
            ax.axis("off")
        else:
            #sort
            sorted_items = sorted(breakdown.items(), key = lambda pair : pair[1], reverse = True)
            genre_names = [name for name, _ in sorted_items]
            percentages = [pct for _, pct in sorted_items]

            ax.barh(genre_names, percentages, color = bar_color)
            ax.set_xlabel("% of swipes")
            ax.invert_yaxis()

            for i, pct in enumerate(percentages):
                ax.text(pct + 1, i, f"{pct}%", va = "center", color = palette['text'])
                
        ax.set_title(title)
        figure.tight_layout()

        return canvas


