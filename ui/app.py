from PySide6.QtWidgets import QMainWindow, QStackedWidget
from .timer_view import TimerView
from .history_view import HistoryView

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus")
        self.resize(760, 720)
        self.setMinimumSize(420, 520)
        self.stack = QStackedWidget()
        self.timer_view = TimerView(self.show_history)
        self.history_view = HistoryView(self.show_timer)
        self.timer_page = self.timer_view
        self.history_page = self.history_view
        self.stack.addWidget(self.timer_view)
        self.stack.addWidget(self.history_view)
        self.setCentralWidget(self.stack)

    def show_history(self):
        self.history_view.refresh()
        self.stack.setCurrentWidget(self.history_page)

    def show_timer(self):
        self.timer_view.refresh_dashboard()
        self.stack.setCurrentWidget(self.timer_page)
