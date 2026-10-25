from datetime import datetime, timedelta

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QProgressBar, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from core.session import Session
from core.timer import FocusTimer
from storage.goals_repository import GoalsRepository
from storage.json_repository import JsonRepository


class GoalEditorDialog(QDialog):
    """Compact editor for the subject processes shown in the TUI."""

    def __init__(self, goals, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Subject processes")
        self.setMinimumWidth(390)
        self.goals = [dict(goal) for goal in goals]
        self.selected_index = None

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(6)
        root.addWidget(QLabel("┌─ DAILY SUBJECT PROCESSES"))
        self.goal_list = QVBoxLayout()
        self.goal_list.setSpacing(2)
        root.addLayout(self.goal_list)

        form = QFrame()
        form.setObjectName("card")
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.addWidget(QLabel("SUBJECT"), 0, 0)
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("C++")
        form_layout.addWidget(self.subject_edit, 0, 1)
        form_layout.addWidget(QLabel("TARGET"), 1, 0)
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0.25, 24)
        self.hours_spin.setSingleStep(0.25)
        self.hours_spin.setValue(1)
        self.hours_spin.setSuffix(" h / day")
        form_layout.addWidget(self.hours_spin, 1, 1)
        root.addWidget(form)

        actions = QHBoxLayout()
        save = QPushButton("[ ADD / UPDATE ]")
        save.setObjectName("chip")
        save.clicked.connect(self.save_goal)
        delete = QPushButton("[ DELETE ]")
        delete.setObjectName("chip")
        delete.clicked.connect(self.delete_selected)
        actions.addWidget(save)
        actions.addWidget(delete)
        root.addLayout(actions)
        close = QDialogButtonBox(QDialogButtonBox.Close)
        close.rejected.connect(self.reject)
        root.addWidget(close)
        self.render_goals()

    def render_goals(self):
        while self.goal_list.count():
            item = self.goal_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for index, goal in enumerate(self.goals):
            row = QPushButton(
                f"{index + 1:02d}  {goal.get('subject', '—'):<18} "
                f"{self.goal_duration(goal.get('target_seconds', 0)):>8} / day"
            )
            row.setObjectName("chip")
            row.clicked.connect(lambda checked=False, value=index: self.select_goal(value))
            self.goal_list.addWidget(row)

    def select_goal(self, index):
        self.selected_index = index
        goal = self.goals[index]
        self.subject_edit.setText(goal.get("subject", ""))
        self.hours_spin.setValue(max(0.25, float(goal.get("target_seconds", 900)) / 3600))

    def save_goal(self):
        subject = self.subject_edit.text().strip()
        if not subject:
            QMessageBox.warning(self, "Missing subject", "Write a subject first.")
            return
        goal = {"subject": subject, "target_seconds": self.hours_spin.value() * 3600, "repeat": True}
        if self.selected_index is None:
            self.goals.append(goal)
        else:
            self.goals[self.selected_index] = goal
        self.selected_index = None
        self.subject_edit.clear()
        self.render_goals()

    def delete_selected(self):
        if self.selected_index is None:
            return
        self.goals.pop(self.selected_index)
        self.selected_index = None
        self.subject_edit.clear()
        self.render_goals()

    @staticmethod
    def goal_duration(seconds):
        hours = float(seconds or 0) / 3600
        return f"{hours:g}h" if hours >= 1 else f"{int(hours * 60)}m"


class DailyGoalDialog(QDialog):
    def __init__(self, seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Daily target")
        self.setMinimumWidth(330)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.addWidget(QLabel("┌─ TOTAL DAILY TARGET"))
        self.hours = QDoubleSpinBox()
        self.hours.setRange(0, 24)
        self.hours.setSingleStep(0.25)
        self.hours.setValue(float(seconds) / 3600 if seconds else 8)
        self.hours.setSuffix(" h / day")
        root.addWidget(self.hours)
        presets = QHBoxLayout()
        for value in (4, 8, 12):
            button = QPushButton(f"[ {value}h ]")
            button.setObjectName("chip")
            button.clicked.connect(lambda checked=False, selected=value: self.hours.setValue(selected))
            presets.addWidget(button)
        root.addLayout(presets)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    @property
    def seconds(self):
        return self.hours.value() * 3600


class TimerView(QWidget):
    def __init__(self, show_history):
        super().__init__()
        self.timer = None
        self.repository = JsonRepository()
        self.goals_repository = GoalsRepository()
        self.show_history = show_history
        self.dashboard_ticks = 0
        self.setFocusPolicy(Qt.StrongFocus)
        self.build_ui()
        self.refresh_dashboard()
        QApplication.instance().installEventFilter(self)
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(100)

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(6)

        top = QHBoxLayout()
        brand = QLabel("FOCUS // SESSION CONTROL")
        brand.setObjectName("brand")
        top.addWidget(brand)
        top.addStretch()
        register = QPushButton("[ R: REGISTRO ]")
        register.setObjectName("chip")
        register.clicked.connect(self.show_history)
        top.addWidget(register)
        root.addLayout(top)

        self.command_status = QLabel("[ ENTER ] start  [ P ] pause  [ F ] finish  [ N ] new  [ R ] register")
        self.command_status.setObjectName("muted")
        root.addWidget(self.command_status)

        dashboard = QHBoxLayout()
        dashboard.setSpacing(6)
        dashboard.addWidget(self.build_state_panel(), 1)
        dashboard.addWidget(self.build_today_panel(), 2)
        root.addLayout(dashboard)

        self.setup = QFrame()
        self.setup.setObjectName("card")
        setup_root = QVBoxLayout(self.setup)
        setup_root.setContentsMargins(8, 6, 8, 6)
        setup_root.setSpacing(3)
        setup_root.addWidget(QLabel("╭─ NEW SESSION"))
        line = QHBoxLayout()
        line.addWidget(QLabel("SUBJECT >"))
        self.subject = QComboBox()
        self.subject.setEditable(True)
        self.subject.setInsertPolicy(QComboBox.NoInsert)
        self.subject.lineEdit().setPlaceholderText("type any subject")
        line.addWidget(self.subject, 1)
        line.addWidget(QLabel("TARGET >"))
        self.duration = QLineEdit("25")
        self.duration.setMaximumWidth(90)
        self.duration.setPlaceholderText("minutes")
        line.addWidget(self.duration)
        setup_root.addLayout(line)
        root.addWidget(self.setup)

        self.session_panel = QFrame()
        self.session_panel.setObjectName("card")
        session_root = QVBoxLayout(self.session_panel)
        session_root.setContentsMargins(8, 6, 8, 6)
        session_root.setSpacing(1)
        session_root.addWidget(QLabel("╭─ SESSION"))
        self.session_grid = QGridLayout()
        self.session_grid.setHorizontalSpacing(12)
        self.session_grid.setVerticalSpacing(1)
        self.subject_label = QLabel("—")
        self.target_label = QLabel("00:00:00")
        self.effective_label = QLabel("00:00:00")
        self.remaining_label = QLabel("00:00:00")
        self.start_info = QLabel("--:--:--")
        self.end_info = QLabel("--:--:--")
        fields = (
            ("SUBJECT", self.subject_label), ("TARGET", self.target_label),
            ("EFFECTIVE", self.effective_label), ("REMAINING", self.remaining_label),
            ("START", self.start_info), ("EST. END", self.end_info),
        )
        for row, (name, value) in enumerate(fields):
            key = QLabel(name.ljust(10))
            key.setObjectName("muted")
            self.session_grid.addWidget(key, row, 0)
            self.session_grid.addWidget(value, row, 1)
        session_root.addLayout(self.session_grid)
        root.addWidget(self.session_panel)

        controls = QHBoxLayout()
        self.start_button = QPushButton("[ ENTER ] START")
        self.start_button.setObjectName("primary")
        self.start_button.clicked.connect(self.start)
        self.pause_button = QPushButton("[ P ] PAUSE")
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.finish_button = QPushButton("[ F ] FINISH")
        self.finish_button.setEnabled(False)
        self.finish_button.clicked.connect(self.finish)
        for button in (self.start_button, self.pause_button, self.finish_button):
            controls.addWidget(button)
        root.addLayout(controls)

        self.status = QLabel("● READY")
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignCenter)
        root.addWidget(self.status)

    def build_state_panel(self):
        panel = QFrame()
        panel.setObjectName("card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(1)
        layout.addWidget(QLabel("╭─ STATE"))
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("timer")
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)
        self.state_subject = QLabel("SUBJECT  —")
        self.state_subject.setObjectName("muted")
        layout.addWidget(self.state_subject)
        self.state_target = QLabel("TARGET   —")
        self.state_target.setObjectName("muted")
        layout.addWidget(self.state_target)
        self.state_mode = QLabel("● READY")
        self.state_mode.setObjectName("status")
        layout.addWidget(self.state_mode)
        return panel

    def build_today_panel(self):
        panel = QFrame()
        panel.setObjectName("card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        title = QHBoxLayout()
        title.addWidget(QLabel("╭─ TODAY / PROCESSES"))
        title.addStretch()
        total = QPushButton("[ TOTAL ]")
        total.setObjectName("chip")
        total.clicked.connect(self.edit_goals)
        subjects = QPushButton("[ SUBJECTS ]")
        subjects.setObjectName("chip")
        subjects.clicked.connect(self.edit_subject_goals)
        title.addWidget(total)
        title.addWidget(subjects)
        layout.addLayout(title)
        self.today_progress = QLabel("TOTAL  0m / —")
        self.today_progress.setObjectName("readout")
        layout.addWidget(self.today_progress)
        header = QHBoxLayout()
        for text in ("PID", "SUBJECT", "TIME", "GRAPH", "%"):
            label = QLabel(text)
            label.setObjectName("muted")
            header.addWidget(label)
        header.setStretch(1, 2)
        header.setStretch(2, 1)
        header.setStretch(3, 1)
        layout.addLayout(header)
        self.subject_goals_layout = QVBoxLayout()
        self.subject_goals_layout.setSpacing(1)
        layout.addLayout(self.subject_goals_layout)
        self.week_progress = QLabel("WEEK  0m / —")
        self.week_progress.setObjectName("muted")
        layout.addWidget(self.week_progress)
        self.week_days = QLabel("0 sessions · 0 subjects")
        self.week_days.setObjectName("muted")
        layout.addWidget(self.week_days)
        return panel

    def edit_goals(self):
        dialog = DailyGoalDialog(self.goals_repository.load_daily_target(), self)
        if dialog.exec() == QDialog.Accepted:
            self.goals_repository.save_daily_target(dialog.seconds)
        self.refresh_dashboard()

    def edit_subject_goals(self):
        dialog = GoalEditorDialog(self.goals_repository.load_subject_goals(), self)
        dialog.exec()
        self.goals_repository.save_subject_goals(dialog.goals)
        self.refresh_subject_options()
        self.refresh_dashboard()

    def refresh_subject_options(self):
        current = self.subject.currentText()
        subjects = [g.get("subject", "").strip() for g in self.goals_repository.load_subject_goals()]
        subjects = [subject for subject in subjects if subject]
        self.subject.blockSignals(True)
        self.subject.clear()
        self.subject.addItems(subjects)
        self.subject.setCurrentText(current)
        self.subject.blockSignals(False)

    def refresh_dashboard(self):
        records = self.repository.load()
        now = datetime.now()
        today = now.date()
        week_start = today - timedelta(days=today.weekday())
        today_records = self.records_on(records, today)
        week_records = [r for r in records if self.record_date(r) and week_start <= self.record_date(r) <= today]
        month_records = [r for r in records if self.record_date(r) and self.record_date(r).year == now.year and self.record_date(r).month == now.month]
        today_seconds = sum(float(r.get("actual_seconds", 0) or 0) for r in today_records)
        week_seconds = sum(float(r.get("actual_seconds", 0) or 0) for r in week_records)
        if self.timer and self.timer.session.started_at and self.timer.session.started_at.date() == today:
            today_seconds += self.timer.elapsed()
            week_seconds += self.timer.elapsed()

        subject_goals = self.goals_repository.load_subject_goals()
        daily_goal = self.goals_repository.load_daily_target()
        if not daily_goal:
            daily_goal = sum(float(g.get("target_seconds", 0) or 0) for g in subject_goals)
        self.today_progress.setText(f"TOTAL  {self.format_hours(today_seconds)} / {self.format_hours(daily_goal) if daily_goal else '—'}")
        self.week_progress.setText(f"WEEK   {self.format_hours(week_seconds)} / {self.format_hours(daily_goal * 7) if daily_goal else '—'}")
        self.week_days.setText(
            f"{len(week_records)} sessions · {len({r.get('subject', '').strip().lower() for r in week_records if r.get('subject')})} subjects"
        )
        self.refresh_subject_options()
        self.render_subject_goals(subject_goals, today_records)

    def render_subject_goals(self, goals, today_records):
        while self.subject_goals_layout.count():
            item = self.subject_goals_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        actual_by_subject = {}
        for record in today_records:
            key = record.get("subject", "").strip().lower()
            actual_by_subject[key] = actual_by_subject.get(key, 0) + float(record.get("actual_seconds", 0) or 0)
        if self.timer:
            key = self.timer.session.subject.strip().lower()
            actual_by_subject[key] = actual_by_subject.get(key, 0) + self.timer.elapsed()
        if not goals:
            empty = QLabel("└─ no subject processes · [ SUBJECTS ] to add")
            empty.setObjectName("muted")
            self.subject_goals_layout.addWidget(empty)
            return
        for index, goal in enumerate(goals, start=1):
            subject = goal.get("subject", "—")
            target = float(goal.get("target_seconds", 0) or 0)
            actual = actual_by_subject.get(subject.strip().lower(), 0)
            percent = min(100, int(actual / target * 100)) if target else 0
            row = QFrame()
            row.setObjectName("processRow")
            line = QHBoxLayout(row)
            line.setContentsMargins(3, 1, 3, 1)
            pid = QLabel(f"{index:02d}")
            pid.setObjectName("muted")
            name = QLabel(subject)
            name.setObjectName("processName")
            advance = QLabel(f"{self.format_hours(actual):>7}/{self.format_hours(target):<7}")
            advance.setObjectName("muted")
            graph = QProgressBar()
            graph.setRange(0, 100)
            graph.setValue(percent)
            graph.setTextVisible(False)
            graph.setFixedWidth(95)
            done = QLabel(f"{percent:3d}%")
            done.setObjectName("processPercent")
            line.addWidget(pid)
            line.addWidget(name, 2)
            line.addWidget(advance, 1)
            line.addWidget(graph, 1)
            line.addWidget(done)
            self.subject_goals_layout.addWidget(row)

    def start(self):
        if self.timer is None:
            subject = self.subject.currentText().strip()
            if not subject:
                QMessageBox.warning(self, "Missing subject", "Write or select a subject.")
                return
            try:
                minutes = float(self.duration.text())
                if minutes <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Invalid target", "Enter a positive number of minutes.")
                return
            self.timer = FocusTimer(Session(subject, minutes * 60))
        self.timer.start()
        self.setup.setVisible(False)
        self.subject.setEnabled(False)
        self.duration.setEnabled(False)
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.finish_button.setEnabled(True)
        self.pause_button.setText("[ P ] PAUSE")
        self.status.setText("● RUNNING")
        self.state_mode.setText("● RUNNING")
        self.welcome_state()
        self.update_session_panel()
        self.refresh_dashboard()

    def toggle_pause(self):
        if not self.timer:
            return
        if self.timer.running:
            self.timer.pause()
            self.pause_button.setText("[ P ] RESUME")
            self.status.setText("● PAUSED · effective clock stopped")
            self.state_mode.setText("● PAUSED")
        else:
            self.timer.start()
            self.pause_button.setText("[ P ] PAUSE")
            self.status.setText("● RUNNING")
            self.state_mode.setText("● RUNNING")

    def finish(self):
        if not self.timer:
            return
        self.timer.finish()
        self.repository.save(self.timer.session)
        self.status.setText("● SAVED · completed" if self.timer.session.completed else "● SAVED")
        self.state_mode.setText("● READY")
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.finish_button.setEnabled(False)
        self.subject.setEnabled(True)
        self.duration.setEnabled(True)
        self.setup.setVisible(True)
        self.timer = None
        self.update_session_panel()
        self.refresh_dashboard()

    def update_session_panel(self):
        if not self.timer:
            self.subject_label.setText("—")
            self.target_label.setText("00:00:00")
            self.effective_label.setText("00:00:00")
            self.remaining_label.setText("00:00:00")
            self.start_info.setText("--:--:--")
            self.end_info.setText("--:--:--")
            self.state_subject.setText("SUBJECT  —")
            self.state_target.setText("TARGET   —")
            self.timer_label.setText("00:00:00")
            return
        session = self.timer.session
        self.subject_label.setText(session.subject)
        self.target_label.setText(self.format_time(session.target_seconds))
        self.effective_label.setText(self.format_time(self.timer.elapsed()))
        self.remaining_label.setText(self.format_time(self.timer.remaining()))
        self.start_info.setText(session.started_at.strftime("%H:%M:%S") if session.started_at else "--:--:--")
        end = self.timer.estimated_end()
        self.end_info.setText(end.strftime("%H:%M:%S") if end else "--:--:--")
        self.state_subject.setText(f"SUBJECT  {session.subject}")
        self.state_target.setText(f"TARGET   {self.format_time(session.target_seconds)}")
        self.timer_label.setText(self.format_time(self.timer.remaining()))

    def welcome_state(self):
        self.command_status.setText("[ ENTER ] running  [ P ] pause  [ F ] finish  [ R ] register")

    def eventFilter(self, obj, event):
        if event.type() != QEvent.KeyPress or not self.isVisible():
            return super().eventFilter(obj, event)
        focus = QApplication.focusWidget()
        if isinstance(focus, (QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox)):
            return super().eventFilter(obj, event)
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.start()
            return True
        if key == Qt.Key_P:
            self.toggle_pause()
            return True
        if key == Qt.Key_F:
            self.finish()
            return True
        if key == Qt.Key_R:
            self.show_history()
            return True
        if key == Qt.Key_N:
            self.new_session()
            return True
        if key == Qt.Key_Escape:
            self.new_session()
            return True
        return super().eventFilter(obj, event)

    def new_session(self):
        if self.timer:
            return
        self.subject.setEnabled(True)
        self.duration.setEnabled(True)
        self.subject.setCurrentText("")
        self.duration.setText("25")
        self.setup.setVisible(True)
        self.status.setText("● READY")
        self.state_mode.setText("● READY")

    def update_ui(self):
        if not self.timer:
            return
        self.update_session_panel()
        self.dashboard_ticks += 1
        if self.dashboard_ticks >= 10:
            self.dashboard_ticks = 0
            self.refresh_dashboard()
        if self.timer.is_complete():
            self.finish()

    def closeEvent(self, event):
        QApplication.instance().removeEventFilter(self)
        super().closeEvent(event)

    @staticmethod
    def record_date(record):
        try:
            return datetime.fromisoformat(record.get("started_at", "")).date()
        except (TypeError, ValueError):
            return None

    @classmethod
    def records_on(cls, records, day):
        return [record for record in records if cls.record_date(record) == day]

    @staticmethod
    def format_hours(seconds):
        total = max(0, int(seconds))
        hours, remainder = divmod(total, 3600)
        minutes = remainder // 60
        if hours:
            return f"{hours}h {minutes:02d}m"
        return f"{minutes}m"

    @staticmethod
    def format_time(seconds):
        seconds = int(max(0, seconds))
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
