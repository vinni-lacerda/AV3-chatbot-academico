"""Guard de autenticação e autorização baseado em perfis (RBAC - RF01), 100% agnóstico ao Flask."""

from application.use_cases.get_current_user import GetCurrentUserUseCase
from domain.entities.user import User, UserRole
from domain.exceptions.domain_exceptions import ForbiddenRoleError, InvalidTokenError
from infrastructure.http.contracts import HttpRequest


class AuthGuard:
    """Extrai o Bearer token de um HttpRequest agnóstico e valida identidade/perfis (RF01)."""

    def __init__(self, get_current_user_use_case: GetCurrentUserUseCase) -> None:
        self._get_current_user_use_case = get_current_user_use_case

    def authenticate(
        self,
        request: HttpRequest,
        required_roles: set[UserRole] | None = None,
    ) -> User:
        auth_header = request.get_header("Authorization")
        if not auth_header:
            raise InvalidTokenError("Header Authorization Bearer não informado.")

        parts = auth_header.strip().split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
            raise InvalidTokenError("Formato de header Authorization inválido. Use 'Bearer <token>'.")

        token = parts[1].strip()
        user = self._get_current_user_use_case.execute_entity(token)

        if required_roles and not user.has_any_role(required_roles):
            sorted_required = sorted([role.value for role in required_roles])
            raise ForbiddenRoleError(sorted_required)

        return user
