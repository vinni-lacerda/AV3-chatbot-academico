"""Controllers HTTP agnósticos para Autenticação e Perfis (RF01).

Zero dependência de Flask ou de qualquer biblioteca externa de validação/serialização.
"""

from application.dtos.auth_dtos import LoginUserInput, RegisterUserInput, UserOutput
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.register_user import RegisterUserUseCase
from domain.entities.user import UserRole
from domain.exceptions.domain_exceptions import ValidationError
from infrastructure.http.contracts import HttpRequest, HttpResponse, IController
from infrastructure.http.middlewares.auth_guard import AuthGuard


class RegisterUserController(IController):
    """Controller agnóstico para cadastro de integrante (`POST /api/v1/auth/register`)."""

    def __init__(self, use_case: RegisterUserUseCase) -> None:
        self._use_case = use_case

    def handle(self, request: HttpRequest) -> HttpResponse:
        body = request.body or {}
        name = str(body.get("name", "")).strip()
        email = str(body.get("email", "")).strip()
        password = str(body.get("password", ""))
        academic_id = body.get("academic_id")

        if not name or not email or not password:
            raise ValidationError("Os campos 'name', 'email' e 'password' são obrigatórios.")

        output = self._use_case.execute(
            RegisterUserInput(
                name=name,
                email=email,
                password=password,
                roles=[UserRole.NOVO_INTEGRANTE],
                academic_id=str(academic_id).strip() if academic_id is not None else None,
            )
        )
        return HttpResponse(status_code=201, body=output.to_dict())


class LoginUserController(IController):
    """Controller agnóstico para login de integrante (`POST /api/v1/auth/login`)."""

    def __init__(self, use_case: AuthenticateUserUseCase) -> None:
        self._use_case = use_case

    def handle(self, request: HttpRequest) -> HttpResponse:
        body = request.body or {}
        email = str(body.get("email", "")).strip()
        password = str(body.get("password", ""))

        if not email or not password:
            raise ValidationError("Os campos 'email' e 'password' são obrigatórios.")

        output = self._use_case.execute(
            LoginUserInput(email=email, password=password)
        )
        return HttpResponse(status_code=200, body=output.to_dict())


class GetMeController(IController):
    """Controller agnóstico para obter dados e permissões do usuário logado (`GET /api/v1/auth/me`)."""

    def __init__(self, auth_guard: AuthGuard) -> None:
        self._auth_guard = auth_guard

    def handle(self, request: HttpRequest) -> HttpResponse:
        user = self._auth_guard.authenticate(request)
        output = UserOutput.from_entity(user)
        return HttpResponse(status_code=200, body=output.to_dict())


class VerifyReviewPermissionController(IController):
    """Controller agnóstico protegido por perfil `responsavel` (`GET /api/v1/auth/permissions/review-check`)."""

    def __init__(self, auth_guard: AuthGuard) -> None:
        self._auth_guard = auth_guard

    def handle(self, request: HttpRequest) -> HttpResponse:
        user = self._auth_guard.authenticate(
            request,
            required_roles={UserRole.RESPONSAVEL},
        )
        return HttpResponse(
            status_code=200,
            body={
                "status": "authorized",
                "user_id": user.id,
                "message": "Usuário possui permissão de revisão de conhecimentos.",
            },
        )
