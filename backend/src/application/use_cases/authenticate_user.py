"""Caso de uso: Autenticar usuário e emitir token de acesso (RF01)."""

from application.dtos.auth_dtos import AuthTokenOutput, LoginUserInput, UserOutput
from domain.exceptions.domain_exceptions import InvalidCredentialsError
from domain.repositories.user_repository import IUserRepository
from domain.services.password_hasher import IPasswordHasher
from domain.services.token_provider import ITokenProvider


class AuthenticateUserUseCase:
    """Responsabilidade única (SRP): Validar credenciais e emitir token de acesso."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        token_provider: ITokenProvider,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider

    def execute(self, data: LoginUserInput) -> AuthTokenOutput:
        normalized_email = data.email.strip().lower()
        user = self._user_repository.find_by_email(normalized_email)

        if user is None:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError("Conta de usuário desativada.")

        if not self._password_hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError()

        sorted_roles = sorted(list(user.roles), key=lambda r: r.value)
        access_token = self._token_provider.create_access_token(
            user_id=user.id,
            email=user.email,
            roles=sorted_roles,
        )

        return AuthTokenOutput(
            access_token=access_token,
            token_type="bearer",
            user=UserOutput.from_entity(user),
        )
