"""Testes unitários da camada HTTP agnóstica (contratos, error mapper, guard e controllers)."""

import pytest

from domain.entities.user import UserRole
from domain.exceptions.domain_exceptions import (
    DomainError,
    ForbiddenRoleError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from infrastructure.container.composition_root import DependencyContainer
from infrastructure.http.contracts import HttpRequest
from infrastructure.http.controllers.health_controller import HealthController
from infrastructure.http.error_mapper import map_domain_error_to_http_response
from infrastructure.persistence.memory.in_memory_user_repository import (
    InMemoryUserRepository,
)
from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher


def test_http_request_case_insensitive_headers() -> None:
    """Deve recuperar headers independentemente de letras maiúsculas ou minúsculas."""
    req = HttpRequest(headers={"Content-Type": "application/json", "X-Custom": "123"})
    assert req.get_header("content-type") == "application/json"
    assert req.get_header("X-CUSTOM") == "123"
    assert req.get_header("Authorization") is None


@pytest.mark.parametrize(
    ("exception", "expected_status", "expected_code"),
    [
        (ValidationError("Dado inválido"), 400, "VALIDATION_ERROR"),
        (UserAlreadyExistsError("a@b.com"), 409, "USER_ALREADY_EXISTS"),
        (InvalidCredentialsError(), 401, "INVALID_CREDENTIALS"),
        (InvalidTokenError(), 401, "INVALID_TOKEN"),
        (ForbiddenRoleError(["responsavel"]), 403, "FORBIDDEN_ROLE"),
        (UserNotFoundError("id-1"), 404, "USER_NOT_FOUND"),
        (DomainError("Erro genérico de domínio"), 400, "DOMAIN_ERROR"),
        (RuntimeError("Falha inesperada"), 500, "INTERNAL_ERROR"),
    ],
)
def test_error_mapper_translates_all_exception_types(
    exception: Exception,
    expected_status: int,
    expected_code: str,
) -> None:
    """Deve mapear todas as exceções de domínio e erros inesperados para HttpResponse."""
    response = map_domain_error_to_http_response(exception)
    assert response.status_code == expected_status
    assert response.body["error_code"] == expected_code


def test_health_controller_returns_200_ok() -> None:
    """Deve retornar status 200 e payload de serviço ativo."""
    controller = HealthController()
    response = controller.handle(HttpRequest())
    assert response.status_code == 200
    assert response.body == {"status": "ok", "service": "passa-o-bastao-backend"}


def test_controllers_validation_errors_on_malformed_requests() -> None:
    """Deve validar campos obrigatórios nos controllers agnósticos."""
    container = DependencyContainer(
        user_repository=InMemoryUserRepository(),
        password_hasher=BcryptPasswordHasher(rounds=4),
    )

    with pytest.raises(ValidationError, match="obrigatórios"):
        container.register_user_controller.handle(HttpRequest(body={"name": "Só Nome"}))

    with pytest.raises(ValidationError, match="obrigatórios"):
        container.register_user_controller.handle(
            HttpRequest(body={"name": "Leoni", "email": "leoni@uni.edu.br"})
        )

    with pytest.raises(ValidationError, match="obrigatórios"):
        container.login_user_controller.handle(HttpRequest(body={"email": "leoni@uni.edu.br"}))


def test_register_user_controller_always_assigns_novo_integrante() -> None:
    """Deve garantir que o controller público atribui novo_integrante mesmo recebendo responsavel."""
    container = DependencyContainer(
        user_repository=InMemoryUserRepository(),
        password_hasher=BcryptPasswordHasher(rounds=4),
    )

    response = container.register_user_controller.handle(
        HttpRequest(
            body={
                "name": "Tentativa Responsavel",
                "email": "tentativa@uni.edu.br",
                "password": "Password123!",
                "roles": [UserRole.RESPONSAVEL.value],
            }
        )
    )
    assert response.status_code == 201
    assert response.body["roles"] == [UserRole.NOVO_INTEGRANTE.value]
    assert response.body["permissions"]["can_review_knowledge"] is False


def test_auth_guard_rejects_missing_or_malformed_authorization_header() -> None:
    """Deve rejeitar requisições sem header Authorization ou sem prefixo Bearer."""
    container = DependencyContainer(
        user_repository=InMemoryUserRepository(),
        password_hasher=BcryptPasswordHasher(rounds=4),
    )

    with pytest.raises(InvalidTokenError, match="não informado"):
        container.get_me_controller.handle(HttpRequest())

    with pytest.raises(InvalidTokenError, match="Formato de header"):
        container.get_me_controller.handle(
            HttpRequest(headers={"Authorization": "Basic abcdef"})
        )
