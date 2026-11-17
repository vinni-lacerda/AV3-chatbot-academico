"""Entidades de domínio relacionadas a usuários e perfis de acesso (RF01)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from domain.exceptions.domain_exceptions import ValidationError


class UserRole(StrEnum):
    """Perfis previstos no projeto Passa o Bastão (RF01).

    - INTEGRANTE: Registra conhecimento por meio da entrevista guiada.
    - NOVO_INTEGRANTE: Consulta orientações aprovadas no chatbot.
    - RESPONSAVEL: Revisa, aprova ou arquiva relatos e mantém atividades.
    """

    INTEGRANTE = "integrante"
    NOVO_INTEGRANTE = "novo_integrante"
    RESPONSAVEL = "responsavel"


@dataclass
class User:
    """Entidade de domínio que representa um integrante do projeto universitário.

    Nota (README RF01): Os papéis podem ser acumulados por uma mesma pessoa no piloto.
    """

    name: str
    email: str
    password_hash: str
    roles: set[UserRole] = field(default_factory=lambda: {UserRole.NOVO_INTEGRANTE})
    id: str = field(default_factory=lambda: str(uuid4()))
    academic_id: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.email = self.email.strip().lower()
        self._validate()

    def _validate(self) -> None:
        if len(self.name) < 2:
            raise ValidationError("O nome do integrante deve ter pelo menos 2 caracteres.")
        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            raise ValidationError("Formato de e-mail inválido.")
        if not self.password_hash:
            raise ValidationError("O hash de senha não pode ser vazio.")
        if not self.roles:
            raise ValidationError("O usuário deve possuir pelo menos um perfil de acesso (RF01).")

    def has_role(self, role: UserRole) -> bool:
        """Verifica se o usuário possui um perfil específico."""
        return role in self.roles

    def has_any_role(self, allowed_roles: set[UserRole]) -> bool:
        """Verifica se o usuário possui ao menos um dos perfis permitidos."""
        return bool(self.roles.intersection(allowed_roles))

    def can_record_knowledge(self) -> bool:
        """RF01/RF02: Verifica se o usuário pode registrar conhecimento na entrevista."""
        return self.is_active and self.has_any_role(
            {UserRole.INTEGRANTE, UserRole.RESPONSAVEL}
        )

    def can_review_knowledge(self) -> bool:
        """RF01/RF04: Verifica se o usuário pode aprovar/revisar conteúdos."""
        return self.is_active and self.has_role(UserRole.RESPONSAVEL)

    def can_query_knowledge(self) -> bool:
        """RF01/RF05: Verifica se o usuário pode consultar a base aprovada."""
        return self.is_active and len(self.roles) > 0
