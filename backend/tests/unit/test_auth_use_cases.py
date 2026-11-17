"""Testes unitários dos casos de uso de autenticação e perfis (RF01).

Estes testes validam Domain + Application sem depender de Flask ou MongoDB.
"""

import pytest

from application.dtos.auth_dtos import LoginUserInput, RegisterUserInput
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.get_current_user import GetCurrentUserUseCase
from application.use_cases.register_user import RegisterUserUseCase
from domain.entities.user import User, UserRole
from domain.exceptions.domain_exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from infrastructure.persistence.memory.in_memory_user_repository import (
    InMemoryUserRepository,
)
from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from infrastructure.security.jwt_token_provider import JwtTokenProvider


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher(rounds=4)


@pytest.fixture
def token_provider() -> JwtTokenProvider:
    return JwtTokenProvider(
        secret_key="test-secret-key-for-unit-tests-minimum-32-bytes",
        algorithm="HS256",
        expire_minutes=30,
    )


def test_register_user_with_multiple_roles_calculates_permissions(
    user_repo: InMemoryUserRepository,
    password_hasher: BcryptPasswordHasher,
) -> None:
    """Deve registrar usuário com múltiplos perfis e calcular todas as permissões."""
    use_case = RegisterUserUseCase(user_repo, password_hasher)

    output = use_case.execute(
        RegisterUserInput(
            name="Leoni Mascarenhas",
            email="Leoni@Universidade.edu.br",
            password="Password123!",
            roles=[UserRole.INTEGRANTE, UserRole.RESPONSAVEL],
            academic_id="12725156424",
        )
    )

    assert output.email == "leoni@universidade.edu.br"
    assert set(output.roles) == {UserRole.INTEGRANTE, UserRole.RESPONSAVEL}
    assert output.permissions.can_record_knowledge is True
    assert output.permissions.can_review_knowledge is True
    assert output.permissions.can_query_knowledge is True


def test_register_duplicate_email_raises_error(
    user_repo: InMemoryUserRepository,
    password_hasher: BcryptPasswordHasher,
) -> None:
    """Deve impedir cadastro duplicado com o mesmo e-mail."""
    use_case = RegisterUserUseCase(user_repo, password_hasher)
    payload = RegisterUserInput(
        name="Vinicius Lacerda",
        email="vinicius@universidade.edu.br",
        password="Password123!",
        roles=[UserRole.NOVO_INTEGRANTE],
    )
    use_case.execute(payload)

    with pytest.raises(UserAlreadyExistsError):
        use_case.execute(payload)


def test_register_short_password_raises_validation_error(
    user_repo: InMemoryUserRepository,
    password_hasher: BcryptPasswordHasher,
) -> None:
    """Deve rejeitar senhas com menos de 8 caracteres."""
    use_case = RegisterUserUseCase(user_repo, password_hasher)

    with pytest.raises(ValidationError):
        use_case.execute(
            RegisterUserInput(
                name="Rafael Stolf",
                email="rafael@universidade.edu.br",
                password="123",
                roles=[UserRole.NOVO_INTEGRANTE],
            )
        )


def test_authenticate_and_get_current_user_flow(
    user_repo: InMemoryUserRepository,
    password_hasher: BcryptPasswordHasher,
    token_provider: JwtTokenProvider,
) -> None:
    """Deve autenticar usuário cadastrado e recuperar seus dados via token JWT."""
    register_uc = RegisterUserUseCase(user_repo, password_hasher)
    auth_uc = AuthenticateUserUseCase(user_repo, password_hasher, token_provider)
    current_user_uc = GetCurrentUserUseCase(user_repo, token_provider)

    register_uc.execute(
        RegisterUserInput(
            name="Hiago Goncalves",
            email="hiago@universidade.edu.br",
            password="SecurePassword99",
            roles=[UserRole.NOVO_INTEGRANTE],
        )
    )

    auth_result = auth_uc.execute(
        LoginUserInput(
            email="hiago@universidade.edu.br",
            password="SecurePassword99",
        )
    )

    assert auth_result.access_token
    assert auth_result.user.permissions.can_review_knowledge is False
    assert auth_result.user.permissions.can_record_knowledge is False
    assert auth_result.user.permissions.can_query_knowledge is True

    current_user = current_user_uc.execute(auth_result.access_token)
    assert current_user.id == auth_result.user.id
    assert current_user.email == "hiago@universidade.edu.br"


def test_authenticate_nonexistent_or_wrong_password_raises_invalid_credentials(
    user_repo: InMemoryUserRepository,
    password_hasher: BcryptPasswordHasher,
    token_provider: JwtTokenProvider,
) -> None:
    """Deve rejeitar login com e-mail não cadastrado ou senha incorreta."""
    register_uc = RegisterUserUseCase(user_repo, password_hasher)
    auth_uc = AuthenticateUserUseCase(user_repo, password_hasher, token_provider)

    with pytest.raises(InvalidCredentialsError):
        auth_uc.execute(
            LoginUserInput(
                email="inexistente@universidade.edu.br",
                password="Password123",
            )
        )

    register_uc.execute(
        RegisterUserInput(
            name="Pedro Murilo",
            email="pedro@universidade.edu.br",
            password="CorrectPassword123",
            roles=[UserRole.INTEGRANTE],
        )
    )

    with pytest.raises(InvalidCredentialsError):
        auth_uc.execute(
            LoginUserInput(
                email="pedro@universidade.edu.br",
                password="WrongPassword999",
            )
        )


def test_authenticate_and_get_current_user_rejects_inactive_user(
    user_repo: InMemoryUserRepository,
    password_hasher: BcryptPasswordHasher,
    token_provider: JwtTokenProvider,
) -> None:
    """Deve bloquear login e uso de token de contas desativadas."""
    inactive_user = User(
        name="Conta Inativa",
        email="inativo@universidade.edu.br",
        password_hash=password_hasher.hash("Password123!"),
        roles={UserRole.INTEGRANTE},
        is_active=False,
    )
    user_repo.create(inactive_user)

    auth_uc = AuthenticateUserUseCase(user_repo, password_hasher, token_provider)
    current_user_uc = GetCurrentUserUseCase(user_repo, token_provider)

    with pytest.raises(InvalidCredentialsError, match="desativada"):
        auth_uc.execute(
            LoginUserInput(
                email="inativo@universidade.edu.br",
                password="Password123!",
            )
        )

    token = token_provider.create_access_token(
        user_id=inactive_user.id,
        email=inactive_user.email,
        roles=[UserRole.INTEGRANTE],
    )
    with pytest.raises(InvalidTokenError, match="inativo"):
        current_user_uc.execute(token)


def test_get_current_user_raises_not_found_when_user_removed(
    user_repo: InMemoryUserRepository,
    token_provider: JwtTokenProvider,
) -> None:
    """Deve lançar UserNotFoundError se o token apontar para um usuário inexistente."""
    current_user_uc = GetCurrentUserUseCase(user_repo, token_provider)
    token = token_provider.create_access_token(
        user_id="id-removido",
        email="removido@universidade.edu.br",
        roles=[UserRole.NOVO_INTEGRANTE],
    )

    with pytest.raises(UserNotFoundError):
        current_user_uc.execute(token)


def test_get_current_user_with_tampered_token_raises_invalid_token(
    user_repo: InMemoryUserRepository,
    token_provider: JwtTokenProvider,
) -> None:
    """Deve rejeitar tokens adulterados ou malformados."""
    current_user_uc = GetCurrentUserUseCase(user_repo, token_provider)

    with pytest.raises(InvalidTokenError):
        current_user_uc.execute("token.invalido.adulterado")
