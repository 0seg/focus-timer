import sys
from PySide6.QtWidgets import QApplication
from ui.app import App
from ui.styles import STYLE

app = QApplication(sys.argv)
app.setStyleSheet(STYLE)
window = App()
window.show()
sys.exit(app.exec())
