"""Repositório de usuários em memória para testes rápidos e substituição LSP."""

from domain.entities.user import User
from domain.exceptions.domain_exceptions import UserAlreadyExistsError
from domain.repositories.user_repository import IUserRepository


class InMemoryUserRepository(IUserRepository):
    """Implementação em memória de IUserRepository (LSP - Liskov Substitution Principle)."""

    def __init__(self) -> None:
        self._users_by_id: dict[str, User] = {}
        self._users_by_email: dict[str, User] = {}

    def create(self, user: User) -> User:
        normalized_email = user.email.strip().lower()
        if normalized_email in self._users_by_email:
            raise UserAlreadyExistsError(normalized_email)
        self._users_by_id[user.id] = user
        self._users_by_email[normalized_email] = user
        return user

    def find_by_email(self, email: str) -> User | None:
        return self._users_by_email.get(email.strip().lower())

    def find_by_id(self, user_id: str) -> User | None:
        return self._users_by_id.get(user_id)
