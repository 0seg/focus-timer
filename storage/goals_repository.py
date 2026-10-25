import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class GoalsRepository:
    """Stores recurring daily goals, independently from session history."""

    def __init__(self, path=None):
        self.path = BASE_DIR / "objetivos.json" if path is None else Path(path)

    def load(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, goals):
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(goals, file, indent=4, ensure_ascii=False)

    def load_daily_target(self):
        goals = self.load()
        for goal in goals:
            if goal.get("type") == "daily_total":
                return float(goal.get("target_seconds", 0) or 0)
        return 0.0

    def save_daily_target(self, seconds):
        goals = [goal for goal in self.load() if goal.get("type") != "daily_total"]
        goals.append({
            "type": "daily_total",
            "target_seconds": float(seconds),
        })
        self.save(goals)

    def load_subject_goals(self):
        return [goal for goal in self.load() if goal.get("type") != "daily_total"]

    def save_subject_goals(self, subject_goals):
        daily = [goal for goal in self.load() if goal.get("type") == "daily_total"]
        self.save(daily + [dict(goal) for goal in subject_goals])
