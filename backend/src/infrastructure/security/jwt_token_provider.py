"""Implementação concreta de emissão e validação de tokens JWT (LSP & DIP)."""

from datetime import datetime, timedelta, timezone

import jwt

from domain.entities.user import UserRole
from domain.exceptions.domain_exceptions import InvalidTokenError
from domain.services.token_provider import ITokenProvider, TokenPayload


class JwtTokenProvider(ITokenProvider):
    """Adaptador para tokens JWT assinados (PyJWT)."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expire_minutes: int = 120,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(
        self,
        user_id: str,
        email: str,
        roles: list[UserRole],
    ) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self._expire_minutes)
        payload = {
            "sub": user_id,
            "email": email,
            "roles": [role.value for role in roles],
            "iat": now,
            "exp": expires_at,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> TokenPayload:
        try:
            decoded = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            subject = decoded.get("sub")
            email = decoded.get("email")
            raw_roles = decoded.get("roles", [])

            if not subject or not email:
                raise InvalidTokenError("Payload do token incompleto.")

            roles = [UserRole(r) for r in raw_roles]
            return TokenPayload(
                subject=str(subject),
                email=str(email),
                roles=roles,
            )
        except jwt.ExpiredSignatureError as exc:
            raise InvalidTokenError("Token de acesso expirado.") from exc
        except (jwt.PyJWTError, ValueError) as exc:
            raise InvalidTokenError("Token de acesso inválido.") from exc
