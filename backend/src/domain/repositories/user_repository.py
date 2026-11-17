"""Contrato (Port) do repositório de usuários (DIP - Dependency Inversion Principle)."""

from abc import ABC, abstractmethod

from domain.entities.user import User


class IUserRepository(ABC):
    """Interface abstrata para persistência da entidade User.

    A camada de Aplicação depende apenas desta abstração (Python puro),
    nunca de detalhes do MongoDB ou de qualquer biblioteca externa.
    """

    @abstractmethod
    def create(self, user: User) -> User:
        """Persiste um novo usuário."""

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        """Busca um usuário pelo e-mail normalizado."""

    @abstractmethod
    def find_by_id(self, user_id: str) -> User | None:
        """Busca um usuário pelo seu identificador único."""
