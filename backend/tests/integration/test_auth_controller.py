"""Testes de integração dos Controllers Agnósticos e do Adaptador Flask (RF01)."""

from flask.testing import FlaskClient
import pytest

from infrastructure.container.composition_root import DependencyContainer
from infrastructure.http.contracts import HttpRequest
from infrastructure.http.error_mapper import map_domain_error_to_http_response
from infrastructure.http.flask.app_factory import create_flask_app
from infrastructure.persistence.memory.in_memory_user_repository import (
    InMemoryUserRepository,
)
from infrastructure.persistence.seed import seed_initial_users
from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher


@pytest.fixture
def container() -> DependencyContainer:
    return DependencyContainer(
        user_repository=InMemoryUserRepository(),
        password_hasher=BcryptPasswordHasher(rounds=4),
    )


@pytest.fixture
def client(container: DependencyContainer) -> FlaskClient:
    app = create_flask_app(container=container)
    app.config["TESTING"] = True
    return app.test_client()


def test_agnostic_controller_runs_without_flask(container: DependencyContainer) -> None:
    """Prova que os controllers em infrastructure/http/controllers funcionam sem o Flask."""
    register_req = HttpRequest(
        body={
            "name": "Integrante Agnóstico",
            "email": "agnostico@universidade.edu.br",
            "password": "Password123!",
            "roles": ["responsavel"],
        }
    )
    reg_res = container.register_user_controller.handle(register_req)
    assert reg_res.status_code == 201
    assert reg_res.body["email"] == "agnostico@universidade.edu.br"
    assert reg_res.body["roles"] == ["novo_integrante"]

    login_res = container.login_user_controller.handle(
        HttpRequest(
            body={
                "email": "agnostico@universidade.edu.br",
                "password": "Password123!",
            }
        )
    )
    token = login_res.body["access_token"]

    try:
        container.verify_review_permission_controller.handle(
            HttpRequest(headers={"Authorization": f"Bearer {token}"})
        )
        pytest.fail("Deveria ter lançado ForbiddenRoleError")
    except Exception as exc:
        mapped = map_domain_error_to_http_response(exc)
        assert mapped.status_code == 403
        assert mapped.body["error_code"] == "FORBIDDEN_ROLE"


def test_flask_openapi_and_swagger_ui_endpoints(client: FlaskClient) -> None:
    """Deve retornar a especificação OpenAPI 3.0.3 em /openapi.json e a página HTML em /docs."""
    spec_response = client.get("/openapi.json")
    assert spec_response.status_code == 200
    spec_data = spec_response.get_json()
    assert spec_data["openapi"] == "3.0.3"
    assert "/api/v1/auth/login" in spec_data["paths"]
    assert "/api/v1/auth/register" in spec_data["paths"]
    assert "/api/v1/auth/me" in spec_data["paths"]
    assert "/api/v1/auth/permissions/review-check" in spec_data["paths"]

    docs_response = client.get("/docs")
    assert docs_response.status_code == 200
    assert "SwaggerUIBundle" in docs_response.get_data(as_text=True)


def test_flask_cors_headers_and_preflight_for_authorized_frontend_origin(
    client: FlaskClient,
) -> None:
    """Deve aplicar headers CORS para origens autorizadas e responder 204 no preflight OPTIONS."""
    preflight = client.options(
        "/api/v1/auth/login",
        headers={"Origin": "http://localhost:5173"},
    )
    assert preflight.status_code == 204
    assert (
        preflight.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"
    )

    unallowed = client.get(
        "/api/v1/health",
        headers={"Origin": "http://origem-nao-autorizada.com"},
    )
    assert unallowed.status_code == 200
    assert unallowed.headers.get("Access-Control-Allow-Origin") is None


def test_flask_healthcheck_endpoint(client: FlaskClient) -> None:
    """Deve responder 200 OK na rota de healthcheck do Flask."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "service": "passa-o-bastao-backend",
    }


def test_flask_adapter_register_login_and_me_endpoints(
    client: FlaskClient,
    container: DependencyContainer,
) -> None:
    """Deve executar o fluxo de cadastro público com perfil novo_integrante e login do seed como responsável."""
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Novo Integrante Publico",
            "email": "publico@universidade.edu.br",
            "password": "Password123!",
            "academic_id": "12725156424",
        },
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.get_json()
    assert reg_data["email"] == "publico@universidade.edu.br"
    assert reg_data["roles"] == ["novo_integrante"]
    assert reg_data["permissions"]["can_review_knowledge"] is False

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "publico@universidade.edu.br",
            "password": "Password123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.get_json()["id"] == reg_data["id"]

    seed_initial_users(container.register_user_use_case)
    seed_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "vinicius@universidade.edu.br",
            "password": "PassaOBastao123!",
        },
    )
    assert seed_login.status_code == 200
    seed_token = seed_login.get_json()["access_token"]

    review_check = client.get(
        "/api/v1/auth/permissions/review-check",
        headers={"Authorization": f"Bearer {seed_token}"},
    )
    assert review_check.status_code == 200


def test_public_registration_cannot_grant_responsavel_and_gets_403_on_review(
    client: FlaskClient,
) -> None:
    """Confirma que uma conta cadastrada recebe 403 na rota de revisão mesmo enviando roles: ['responsavel']."""
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Tentativa Invasor Responsavel",
            "email": "invasor@universidade.edu.br",
            "password": "Password123!",
            "roles": ["responsavel"],
        },
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.get_json()
    assert reg_data["roles"] == ["novo_integrante"]
    assert reg_data["permissions"]["can_review_knowledge"] is False

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invasor@universidade.edu.br",
            "password": "Password123!",
        },
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]

    review_check = client.get(
        "/api/v1/auth/permissions/review-check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert review_check.status_code == 403
    assert review_check.get_json()["error_code"] == "FORBIDDEN_ROLE"


def test_flask_error_responses_for_conflict_and_unauthorized(
    client: FlaskClient,
) -> None:
    """Deve traduzir exceções de domínio em status HTTP 400, 401 e 409 com headers apropriados."""
    payload = {
        "name": "Vinicius Lacerda",
        "email": "vinicius.novo@universidade.edu.br",
        "password": "Password123!",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    conflict = client.post("/api/v1/auth/register", json=payload)
    assert conflict.status_code == 409
    assert conflict.get_json()["error_code"] == "USER_ALREADY_EXISTS"

    invalid_login = client.post(
        "/api/v1/auth/login",
        json={"email": "vinicius.novo@universidade.edu.br", "password": " errada "},
    )
    assert invalid_login.status_code == 401
    assert invalid_login.headers.get("WWW-Authenticate") == "Bearer"

    unauthenticated_me = client.get("/api/v1/auth/me")
    assert unauthenticated_me.status_code == 401
    assert unauthenticated_me.headers.get("WWW-Authenticate") == "Bearer"
