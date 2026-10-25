from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from storage.json_repository import JsonRepository


class HistoryView(QWidget):
    def __init__(self, show_timer):
        super().__init__()
        self.repository = JsonRepository()
        self.show_timer = show_timer
        self.build_ui()
        self.refresh()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(6)

        top = QHBoxLayout()
        top.addWidget(QLabel("FOCUS // REGISTRO"))
        top.addStretch()
        back = QPushButton("[ ESC ] BACK")
        back.setObjectName("chip")
        back.clicked.connect(self.show_timer)
        top.addWidget(back)
        root.addLayout(top)

        self.summary = QLabel("")
        self.summary.setObjectName("readout")
        root.addWidget(self.summary)
        self.subtitle = QLabel("[ ↑ ↓ ] select  [ DELETE ] remove  [ ESC ] back")
        self.subtitle.setObjectName("muted")
        root.addWidget(self.subtitle)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(("DATE", "SUBJECT", "EFFECTIVE", "TARGET", "STATUS"))
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table)

        actions = QHBoxLayout()
        delete = QPushButton("[ DELETE SELECTED ]")
        delete.setObjectName("chip")
        delete.clicked.connect(self.delete_selected)
        clear = QPushButton("[ CLEAR LOG ]")
        clear.setObjectName("chip")
        clear.clicked.connect(self.clear_history)
        actions.addWidget(delete)
        actions.addWidget(clear)
        actions.addStretch()
        root.addLayout(actions)

    def refresh(self):
        records = self.repository.load()
        now = datetime.now()
        month_records = [r for r in records if self.record_date(r) and self.record_date(r).year == now.year and self.record_date(r).month == now.month]
        seconds = sum(float(r.get("actual_seconds", 0) or 0) for r in month_records)
        self.summary.setText(
            f"MONTH {now.strftime('%Y-%m')}   {self.format_hours(seconds)}   "
            f"{len(month_records)} sessions   {len({r.get('subject', '').lower() for r in month_records if r.get('subject')})} subjects"
        )
        self.table.setRowCount(0)
        for index, record in sorted(enumerate(records), key=lambda pair: self.record_sort_key(pair[1]), reverse=True):
            row = self.table.rowCount()
            self.table.insertRow(row)
            date = self.format_date(record.get("started_at"))
            actual = float(record.get("actual_seconds", 0) or 0)
            target = float(record.get("target_seconds", 0) or 0)
            percent = min(100, int(actual / target * 100)) if target else 0
            values = (
                date,
                record.get("subject", "—"),
                self.format_time(actual),
                self.format_time(target),
                f"{self.graph(percent)} {percent:3d}%" + ("  ✓" if record.get("completed") else ""),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, index)
                self.table.setItem(row, column, item)
        self.table.resizeRowsToContents()

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No selection", "Select a session first.")
            return
        index = self.table.item(row, 0).data(Qt.UserRole)
        answer = QMessageBox.question(
            self,
            "Delete session",
            "Delete the selected session? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.repository.delete_at(int(index))
            self.refresh()

    def clear_history(self):
        records = self.repository.load()
        if not records:
            return
        answer = QMessageBox.question(
            self,
            "Clear log",
            f"Delete {len(records)} recorded sessions? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.repository.clear()
            self.refresh()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.show_timer()
            return
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
            return
        super().keyPressEvent(event)

    @staticmethod
    def record_date(record):
        try:
            return datetime.fromisoformat(record.get("started_at", "")).date()
        except (TypeError, ValueError):
            return None

    @classmethod
    def record_sort_key(cls, record):
        return cls.record_date(record) or datetime.min.date()

    @staticmethod
    def format_date(value):
        try:
            return datetime.fromisoformat(value).strftime("%d/%m/%y")
        except (TypeError, ValueError):
            return "--/--/--"

    @staticmethod
    def graph(percent, width=5):
        filled = round(percent / 100 * width)
        return "█" * filled + "░" * (width - filled)

    @staticmethod
    def format_hours(seconds):
        total = int(seconds)
        hours, remainder = divmod(total, 3600)
        minutes = remainder // 60
        return f"{hours}h {minutes:02d}m" if hours else f"{minutes}m"

    @staticmethod
    def format_time(seconds):
        seconds = int(max(0, float(seconds or 0)))
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
