import time
from datetime import datetime, timedelta
from .session import Session

class FocusTimer:
    def __init__(self, session: Session):
        self.session = session
        self.running = False
        self._last_tick = None
        self._pause_started = None

    def start(self):
        if self.running:
            return
        now = datetime.now()
        if self.session.started_at is None:
            self.session.started_at = now
        if self._pause_started is not None:
            pause_seconds = time.perf_counter() - self._pause_started
            self.session.paused_seconds += pause_seconds
            pause = self.session.pauses[-1]
            pause["ended_at"] = now.isoformat(timespec="seconds")
            pause["duration_seconds"] = round(pause_seconds, 2)
            self._pause_started = None
        self._last_tick = time.perf_counter()
        self.running = True

    def pause(self):
        if not self.running:
            return
        self._update_elapsed()
        self.running = False
        self._pause_started = time.perf_counter()
        self.session.pauses.append({
            "started_at": datetime.now().isoformat(timespec="seconds")
        })

    def _update_elapsed(self):
        if self.running:
            now = time.perf_counter()
            self.session.actual_seconds += now - self._last_tick
            self._last_tick = now

    def elapsed(self):
        value = self.session.actual_seconds
        if self.running:
            value += time.perf_counter() - self._last_tick
        return value

    def remaining(self):
        return max(0.0, self.session.target_seconds - self.elapsed())

    def estimated_end(self):
        if self.session.started_at is None:
            return None
        return datetime.now() + timedelta(seconds=self.remaining())

    def finish(self):
        if self.running:
            self._update_elapsed()
        self.running = False
        self.session.finished_at = datetime.now()
        self.session.completed = self.session.actual_seconds >= self.session.target_seconds

    def is_complete(self):
        return self.remaining() <= 0
