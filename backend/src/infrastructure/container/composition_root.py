"""Composition Root (Container de Injeção de Dependências em Python puro).

Conecta as abstrações de Domínio às implementações concretas de Infraestrutura
e instancia os Casos de Uso e Controllers agnósticos.
"""

from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.get_current_user import GetCurrentUserUseCase
from application.use_cases.register_user import RegisterUserUseCase
from domain.repositories.user_repository import IUserRepository
from domain.services.password_hasher import IPasswordHasher
from domain.services.token_provider import ITokenProvider
from infrastructure.config.settings import Settings, get_settings
from infrastructure.http.controllers.auth_controller import (
    GetMeController,
    LoginUserController,
    RegisterUserController,
    VerifyReviewPermissionController,
)
from infrastructure.http.controllers.docs_controller import OpenApiSpecController
from infrastructure.http.controllers.health_controller import HealthController
from infrastructure.http.middlewares.auth_guard import AuthGuard
from infrastructure.persistence.mongodb.connection import MongoDBConnectionManager
from infrastructure.persistence.mongodb.repositories.mongo_user_repository import (
    MongoUserRepository,
)
from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from infrastructure.security.jwt_token_provider import JwtTokenProvider


class DependencyContainer:
    """Container explícito de dependências seguindo o Dependency Inversion Principle (DIP)."""

    def __init__(
        self,
        settings: Settings | None = None,
        user_repository: IUserRepository | None = None,
        password_hasher: IPasswordHasher | None = None,
        token_provider: ITokenProvider | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._mongo_manager: MongoDBConnectionManager | None = None

        if user_repository is not None:
            self.user_repository = user_repository
        else:
            self._mongo_manager = MongoDBConnectionManager(self.settings)
            self.user_repository = MongoUserRepository(self._mongo_manager.database)

        self.password_hasher = password_hasher or BcryptPasswordHasher()
        self.token_provider = token_provider or JwtTokenProvider(
            secret_key=self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
            expire_minutes=self.settings.jwt_access_token_expire_minutes,
        )

        self.register_user_use_case = RegisterUserUseCase(
            user_repository=self.user_repository,
            password_hasher=self.password_hasher,
        )
        self.authenticate_user_use_case = AuthenticateUserUseCase(
            user_repository=self.user_repository,
            password_hasher=self.password_hasher,
            token_provider=self.token_provider,
        )
        self.get_current_user_use_case = GetCurrentUserUseCase(
            user_repository=self.user_repository,
            token_provider=self.token_provider,
        )

        self.auth_guard = AuthGuard(self.get_current_user_use_case)
        self.health_controller = HealthController()
        self.openapi_spec_controller = OpenApiSpecController()
        self.register_user_controller = RegisterUserController(
            self.register_user_use_case
        )
        self.login_user_controller = LoginUserController(
            self.authenticate_user_use_case
        )
        self.get_me_controller = GetMeController(self.auth_guard)
        self.verify_review_permission_controller = VerifyReviewPermissionController(
            self.auth_guard
        )
