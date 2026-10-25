import json
from pathlib import Path
from dataclasses import asdict
from core.session import Session

BASE_DIR = Path(__file__).resolve().parent.parent


class JsonRepository:
    def __init__(self, path=None):
        self.path = BASE_DIR / "registros.json" if path is None else Path(path)

    def save(self, session: Session):
        records = self.load()
        records.append(asdict(session))
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=4, ensure_ascii=False, default=str)

    def load(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    def delete_at(self, index):
        records = self.load()
        if not 0 <= index < len(records):
            return False
        records.pop(index)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=4, ensure_ascii=False, default=str)
        return True

    def clear(self):
        with self.path.open("w", encoding="utf-8") as file:
            json.dump([], file, indent=4, ensure_ascii=False)
