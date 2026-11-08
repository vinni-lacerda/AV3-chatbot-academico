"""Exceções da camada de domínio."""


class DomainError(Exception):
    """Exceção base para violações de regra de negócio no domínio."""


class ValidationError(DomainError):
    """Dados de entrada violam invariantes da entidade."""


class UserAlreadyExistsError(DomainError):
    """Tentativa de registrar usuário com e-mail já cadastrado."""

    def __init__(self, email: str) -> None:
        super().__init__(f"Já existe um integrante cadastrado com o e-mail '{email}'.")
        self.email = email


class InvalidCredentialsError(DomainError):
    """Credenciais de login inválidas ou usuário inativo."""

    def __init__(self, message: str = "E-mail ou senha inválidos.") -> None:
        super().__init__(message)


class UserNotFoundError(DomainError):
    """Usuário não encontrado na base."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Usuário '{identifier}' não encontrado.")
        self.identifier = identifier


class InvalidTokenError(DomainError):
    """Token de autenticação ausente, expirado ou inválido."""

    def __init__(self, message: str = "Token de acesso inválido ou expirado.") -> None:
        super().__init__(message)


class ForbiddenRoleError(DomainError):
    """Usuário autenticado não possui o perfil exigido para a operação (RF01)."""

    def __init__(self, required_roles: list[str]) -> None:
        roles_str = ", ".join(required_roles)
        super().__init__(
            f"Acesso negado. Esta operação requer um dos seguintes perfis: {roles_str}."
        )
        self.required_roles = required_roles
