"""Implementação concreta do repositório de usuários em MongoDB (LSP & DIP)."""

from datetime import datetime, timezone
from typing import Any

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from domain.entities.user import User, UserRole
from domain.exceptions.domain_exceptions import UserAlreadyExistsError
from domain.repositories.user_repository import IUserRepository


class MongoUserRepository(IUserRepository):
    """Adaptador de persistência da entidade User para uma coleção MongoDB."""

    COLLECTION_NAME = "users"

    def __init__(self, database: Database) -> None:
        self._collection = database[self.COLLECTION_NAME]

    def create(self, user: User) -> User:
        document = self._to_document(user)
        try:
            self._collection.insert_one(document)
        except DuplicateKeyError as exc:
            raise UserAlreadyExistsError(user.email) from exc
        return user

    def find_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        doc = self._collection.find_one({"email": normalized_email})
        if doc is None:
            return None
        return self._to_entity(doc)

    def find_by_id(self, user_id: str) -> User | None:
        doc = self._collection.find_one({"id": user_id})
        if doc is None:
            return None
        return self._to_entity(doc)

    @staticmethod
    def _to_document(user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "password_hash": user.password_hash,
            "roles": sorted([role.value for role in user.roles]),
            "academic_id": user.academic_id,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    @staticmethod
    def _to_entity(doc: dict[str, Any]) -> User:
        created_at = doc.get("created_at") or datetime.now(timezone.utc)
        updated_at = doc.get("updated_at") or datetime.now(timezone.utc)
        roles = {UserRole(r) for r in doc.get("roles", [UserRole.NOVO_INTEGRANTE.value])}
        return User(
            id=str(doc["id"]),
            name=str(doc["name"]),
            email=str(doc["email"]),
            password_hash=str(doc["password_hash"]),
            roles=roles,
            academic_id=doc.get("academic_id"),
            is_active=bool(doc.get("is_active", True)),
            created_at=created_at,
            updated_at=updated_at,
        )
