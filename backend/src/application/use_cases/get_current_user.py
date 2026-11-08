"""Caso de uso: Obter usuário atual a partir do token de acesso (RF01)."""

from application.dtos.auth_dtos import UserOutput
from domain.entities.user import User
from domain.exceptions.domain_exceptions import InvalidTokenError, UserNotFoundError
from domain.repositories.user_repository import IUserRepository
from domain.services.token_provider import ITokenProvider


class GetCurrentUserUseCase:
    """Responsabilidade única (SRP): Validar token e recuperar a entidade User ativa."""

    def __init__(
        self,
        user_repository: IUserRepository,
        token_provider: ITokenProvider,
    ) -> None:
        self._user_repository = user_repository
        self._token_provider = token_provider

    def execute_entity(self, token: str) -> User:
        payload = self._token_provider.decode_access_token(token)
        user = self._user_repository.find_by_id(payload.subject)

        if user is None:
            raise UserNotFoundError(payload.subject)

        if not user.is_active:
            raise InvalidTokenError("Usuário inativo.")

        return user

    def execute(self, token: str) -> UserOutput:
        user = self.execute_entity(token)
        return UserOutput.from_entity(user)
