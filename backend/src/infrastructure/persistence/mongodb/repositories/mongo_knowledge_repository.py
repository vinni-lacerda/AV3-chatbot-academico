"""Implementação MongoDB com atualização atômica de cada histórico."""

from pymongo import DESCENDING
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError


class MongoKnowledgeRepository:
    def __init__(self, database: Database) -> None:
        self._activities = database["activities"]
        self._records = database["knowledge_records"]
        self._records.create_index("activity_id")
        self._records.create_index("author.id")
        self._records.create_index("versions.status")

    def activities(self) -> list[dict]:
        return list(self._activities.find().sort("title"))

    def activity(self, identifier: str) -> dict | None:
        return self._activities.find_one({"_id": identifier})

    def create_activity(self, activity: dict) -> None:
        self._activities.insert_one(activity)

    def record(self, identifier: str) -> dict | None:
        return self._records.find_one({"_id": identifier})

    def records(self, filters: dict):
        return self._records.find(filters).sort("updated_at", DESCENDING)

    def insert_record(self, record: dict) -> bool:
        try:
            self._records.insert_one(record)
        except DuplicateKeyError:
            return False
        return True

    def replace_record(self, record: dict, previous_revision: int) -> bool:
        result = self._records.replace_one(
            {"_id": record["_id"], "revision": previous_revision}, record
        )
        return result.matched_count == 1
