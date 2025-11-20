from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from structlog import get_logger

logger = get_logger()

class InMemoryStore:
    def __init__(self) -> None:
        self.patterns: dict[UUID, dict[str, Any]] = {}
        self.collections: dict[UUID, dict[str, Any]] = {}
        self.collection_patterns: defaultdict[UUID, list[UUID]] = defaultdict(list)
        self.likes: defaultdict[UUID, set[UUID]] = defaultdict(set)
        self.sessions: dict[UUID, dict[str, Any]] = {}
        self.exports: dict[UUID, dict[str, Any]] = {}

    def _timestamp(self) -> datetime:
        return datetime.now(timezone.utc)

    def create_pattern(self, payload: dict[str, Any]) -> dict[str, Any]:
        pattern_id = uuid4()
        now = self._timestamp()
        record = {
            **payload,
            "id": pattern_id,
            "likes_count": 0,
            "views_count": 0,
            "forked_from": payload.get("forked_from"),
            "created_at": now,
            "updated_at": now,
        }
        self.patterns[pattern_id] = record
        logger.info("pattern_created", pattern_id=str(pattern_id))
        return record

    def update_pattern(self, pattern_id: UUID, updates: dict[str, Any]) -> dict[str, Any]:
        record = self.patterns[pattern_id]
        record.update({k: v for k, v in updates.items() if v is not None})
        record["updated_at"] = self._timestamp()
        logger.info("pattern_updated", pattern_id=str(pattern_id))
        return record

    def like_pattern(self, pattern_id: UUID, user_id: UUID | None) -> int:
        bucket = self.likes[pattern_id]
        if user_id is not None:
            bucket.add(user_id)
        self.patterns[pattern_id]["likes_count"] = len(bucket)
        return self.patterns[pattern_id]["likes_count"]

    def unlike_pattern(self, pattern_id: UUID, user_id: UUID | None) -> int:
        bucket = self.likes[pattern_id]
        if user_id is not None and user_id in bucket:
            bucket.remove(user_id)
        self.patterns[pattern_id]["likes_count"] = len(bucket)
        return self.patterns[pattern_id]["likes_count"]

    def fork_pattern(self, parent_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        return self.create_pattern({**payload, "forked_from": parent_id})

    def create_collection(self, payload: dict[str, Any]) -> dict[str, Any]:
        collection_id = uuid4()
        record = {
            **payload,
            "id": collection_id,
            "created_at": self._timestamp(),
        }
        self.collections[collection_id] = record
        logger.info("collection_created", collection_id=str(collection_id))
        return record

    def add_to_collection(self, collection_id: UUID, pattern_ids: list[UUID]) -> None:
        self.collection_patterns[collection_id].extend(pattern_ids)
        logger.info("collection_patterns_added", collection_id=str(collection_id), count=len(pattern_ids))

    def create_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        session_id = uuid4()
        record = {
            **payload,
            "id": session_id,
            "created_at": self._timestamp(),
            "participants": [],
            "is_active": True,
        }
        self.sessions[session_id] = record
        logger.info("session_created", session_id=str(session_id))
        return record

    def create_export(self, payload: dict[str, Any]) -> dict[str, Any]:
        export_id = uuid4()
        record = {
            **payload,
            "export_id": export_id,
            "status": "queued",
            "created_at": self._timestamp(),
        }
        self.exports[export_id] = record
        logger.info("export_enqueued", export_id=str(export_id))
        return record


store = InMemoryStore()
