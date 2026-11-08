"""Data Transfer Objects (DTOs) da camada de aplicação para autenticação (RF01).

100% Python padrão (stdlib), sem dependência de bibliotecas externas.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from domain.entities.user import User, UserRole


@dataclass(frozen=True)
class RegisterUserInput:
    """Dados de entrada para registro de um integrante."""

    name: str
    email: str
    password: str
    roles: list[UserRole]
    academic_id: str | None = None


@dataclass(frozen=True)
class LoginUserInput:
    """Credenciais de entrada para autenticação."""

    email: str
    password: str


@dataclass(frozen=True)
class UserPermissionsOutput:
    """Permissões derivadas dos perfis do usuário (RF01)."""

    can_record_knowledge: bool
    can_review_knowledge: bool
    can_query_knowledge: bool

    def to_dict(self) -> dict[str, bool]:
        return {
            "can_record_knowledge": self.can_record_knowledge,
            "can_review_knowledge": self.can_review_knowledge,
            "can_query_knowledge": self.can_query_knowledge,
        }


@dataclass(frozen=True)
class UserOutput:
    """Representação pública segura de um usuário autenticado ou recém-criado."""

    id: str
    name: str
    email: str
    roles: list[UserRole]
    academic_id: str | None
    is_active: bool
    permissions: UserPermissionsOutput
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserOutput":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            roles=sorted(list(user.roles), key=lambda r: r.value),
            academic_id=user.academic_id,
            is_active=user.is_active,
            permissions=UserPermissionsOutput(
                can_record_knowledge=user.can_record_knowledge(),
                can_review_knowledge=user.can_review_knowledge(),
                can_query_knowledge=user.can_query_knowledge(),
            ),
            created_at=user.created_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "roles": [role.value for role in self.roles],
            "academic_id": self.academic_id,
            "is_active": self.is_active,
            "permissions": self.permissions.to_dict(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class AuthTokenOutput:
    """Resposta do caso de uso de login contendo o token JWT e dados do usuário."""

    access_token: str
    token_type: str
    user: UserOutput

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "user": self.user.to_dict(),
        }
