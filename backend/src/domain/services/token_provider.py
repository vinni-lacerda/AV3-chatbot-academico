"""Contrato (Port) para emissão e leitura de tokens de acesso (ISP & DIP)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.entities.user import UserRole


@dataclass(frozen=True)
class TokenPayload:
    """Dados extraídos de um token de acesso validado."""

    subject: str
    email: str
    roles: list[UserRole]


class ITokenProvider(ABC):
    """Interface para geração e decodificação de tokens de autenticação."""

    @abstractmethod
    def create_access_token(
        self,
        user_id: str,
        email: str,
        roles: list[UserRole],
    ) -> str:
        """Emite um token assinado contendo identidade e perfis do usuário."""

    @abstractmethod
    def decode_access_token(self, token: str) -> TokenPayload:
        """Valida e decodifica o token, lançando InvalidTokenError se inválido."""
