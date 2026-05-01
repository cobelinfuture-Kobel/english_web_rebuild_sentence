import json
from datetime import datetime
from pathlib import Path


class AttemptsStore:
    def __init__(self, path, users_store=None, now_fn=None):
        self.path = Path(path)
        self.users_store = users_store
        self.now_fn = now_fn or datetime.now
        self._ensure_file()

    def create_attempt(
        self,
        user_id,
        sentence_id,
        level,
        pattern,
        user_answer,
        correct_answer,
        is_correct,
    ):
        if self.users_store and not self.users_store.user_exists(user_id):
            raise ValueError("User not found")

        attempts = self._load()
        attempt = {
            "id": self._next_id(attempts),
            "user_id": user_id,
            "sentence_id": sentence_id,
            "level": level,
            "pattern": pattern,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": bool(is_correct),
            "created_at": self.now_fn().isoformat(),
        }
        attempts.append(attempt)
        self._save(attempts)
        return attempt

    def get_user_attempts(self, user_id):
        attempts = [attempt for attempt in self._load() if attempt["user_id"] == user_id]
        return sorted(attempts, key=lambda item: item["created_at"], reverse=True)

    def get_user_stats(self, user_id):
        attempts = [attempt for attempt in self._load() if attempt["user_id"] == user_id]
        return {
            "user_id": user_id,
            **self._build_stats(attempts),
            "by_level": self._group_stats(attempts, "level"),
            "by_pattern": self._group_stats(attempts, "pattern"),
        }

    def get_user_weak_patterns(self, user_id, min_attempts=5, threshold=0.7):
        pattern_stats = self.get_user_stats(user_id)["by_pattern"]
        weak_patterns = []

        for pattern, stats in pattern_stats.items():
            if stats["total_attempts"] < min_attempts:
                continue
            if stats["accuracy"] >= threshold:
                continue

            weak_patterns.append({"pattern": pattern, **stats})

        weak_patterns.sort(key=lambda item: (item["accuracy"], -item["wrong_attempts"]))

        return {
            "user_id": user_id,
            "min_attempts": min_attempts,
            "threshold": threshold,
            "weak_patterns": weak_patterns,
        }

    def _ensure_file(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self):
        self._ensure_file()
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, attempts):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(attempts, f, indent=4, ensure_ascii=False)

    def _build_stats(self, attempts):
        total_attempts = len(attempts)
        correct_attempts = sum(1 for attempt in attempts if attempt.get("is_correct"))
        wrong_attempts = total_attempts - correct_attempts
        accuracy = correct_attempts / total_attempts if total_attempts else 0
        return {
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "wrong_attempts": wrong_attempts,
            "accuracy": accuracy,
        }

    def _group_stats(self, attempts, field_name):
        grouped = {}
        for attempt in attempts:
            group_key = attempt.get(field_name)
            if group_key is None:
                continue
            grouped.setdefault(group_key, []).append(attempt)

        return {
            group_key: self._build_stats(group_attempts)
            for group_key, group_attempts in grouped.items()
        }

    def _next_id(self, attempts):
        max_number = 0
        for attempt in attempts:
            attempt_id = attempt.get("id", "")
            if not attempt_id.startswith("attempt_"):
                continue
            try:
                max_number = max(max_number, int(attempt_id.split("_")[1]))
            except (IndexError, ValueError):
                continue
        return f"attempt_{max_number + 1:03d}"
