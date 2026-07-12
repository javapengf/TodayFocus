import json
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"
ARCHIVE_RETENTION_DAYS = 7


class DataManager:
    def __init__(self):
        self._data = self._load()
        self._check_daily_reset()

    # ── File I/O ──────────────────────────────────

    def _load(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._empty_structure()

    def _save(self):
        tmp = DATA_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        tmp.replace(DATA_FILE)

    @staticmethod
    def _empty_structure():
        return {
            "last_date": date.today().isoformat(),
            "today_items": [],
            "archive": [],
        }

    # ── Daily Reset ───────────────────────────────

    def _check_daily_reset(self):
        today = date.today().isoformat()
        if self._data["last_date"] != today:
            if self._data["today_items"]:
                self._data["archive"].append(
                    {"date": self._data["last_date"], "items": self._data["today_items"]}
                )
            cutoff = (date.today() - timedelta(days=ARCHIVE_RETENTION_DAYS)).isoformat()
            self._data["archive"] = [a for a in self._data["archive"] if a["date"] >= cutoff]
            self._data["today_items"] = []
            self._data["last_date"] = today
            self._save()

    # ── CRUD ──────────────────────────────────────

    def add_item(self, text, priority="normal"):
        item = {
            "id": uuid.uuid4().hex[:8],
            "text": text,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        if priority == "high":
            self._data["today_items"].insert(0, item)
        else:
            self._data["today_items"].append(item)
        self._save()
        return item

    def toggle_complete(self, item_id):
        for item in self._data["today_items"]:
            if item["id"] == item_id:
                item["completed"] = not item["completed"]
                self._save()
                return item
        return None

    def delete_item(self, item_id):
        before = len(self._data["today_items"])
        self._data["today_items"] = [i for i in self._data["today_items"] if i["id"] != item_id]
        if len(self._data["today_items"]) < before:
            self._save()
            return True
        return False

    def get_items(self):
        return list(self._data["today_items"])

    def get_stats(self):
        items = self._data["today_items"]
        return len(items), sum(1 for i in items if i["completed"])
