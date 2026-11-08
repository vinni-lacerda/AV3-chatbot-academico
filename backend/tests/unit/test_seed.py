"""Testes unitários do seed de usuários iniciais."""

from application.dtos.auth_dtos import LoginUserInput
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.register_user import RegisterUserUseCase
from infrastructure.persistence.memory.in_memory_user_repository import (
    InMemoryUserRepository,
)
from infrastructure.persistence.seed import (
    DEFAULT_SEED_PASSWORD,
    INITIAL_USERS_SEED,
    seed_initial_users,
)
from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from infrastructure.security.jwt_token_provider import JwtTokenProvider


def test_seed_initial_users_is_idempotent_and_allows_login() -> None:
    """Deve criar todos os usuários do seed na primeira execução, ignorar na segunda e permitir login."""
    repo = InMemoryUserRepository()
    hasher = BcryptPasswordHasher(rounds=4)
    tokens = JwtTokenProvider(secret_key="chave-secreta-de-teste-com-32-bytes-minimo")

    register_uc = RegisterUserUseCase(repo, hasher)
    auth_uc = AuthenticateUserUseCase(repo, hasher, tokens)

    first_run = seed_initial_users(register_uc)
    assert len(first_run) == len(INITIAL_USERS_SEED)

    second_run = seed_initial_users(register_uc)
    assert len(second_run) == 0

    auth_result = auth_uc.execute(
        LoginUserInput(
            email="leoni@universidade.edu.br",
            password=DEFAULT_SEED_PASSWORD,
        )
    )
    assert auth_result.user.academic_id == "12725156424"
    assert auth_result.user.permissions.can_review_knowledge is True
