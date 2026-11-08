"""Mapeador agnóstico de exceções de domínio para HttpResponse."""

from domain.exceptions.domain_exceptions import (
    DomainError,
    ForbiddenRoleError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from infrastructure.http.contracts import HttpResponse


def map_domain_error_to_http_response(exc: Exception) -> HttpResponse:
    """Traduz exceções do domínio em respostas HTTP sem acoplamento ao Flask."""
    if isinstance(exc, ValidationError):
        return HttpResponse(
            status_code=400,
            body={"detail": str(exc), "error_code": "VALIDATION_ERROR"},
        )

    if isinstance(exc, UserAlreadyExistsError):
        return HttpResponse(
            status_code=409,
            body={"detail": str(exc), "error_code": "USER_ALREADY_EXISTS"},
        )

    if isinstance(exc, InvalidCredentialsError):
        return HttpResponse(
            status_code=401,
            body={"detail": str(exc), "error_code": "INVALID_CREDENTIALS"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    if isinstance(exc, InvalidTokenError):
        return HttpResponse(
            status_code=401,
            body={"detail": str(exc), "error_code": "INVALID_TOKEN"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    if isinstance(exc, ForbiddenRoleError):
        return HttpResponse(
            status_code=403,
            body={"detail": str(exc), "error_code": "FORBIDDEN_ROLE"},
        )

    if isinstance(exc, UserNotFoundError):
        return HttpResponse(
            status_code=404,
            body={"detail": str(exc), "error_code": "USER_NOT_FOUND"},
        )

    if isinstance(exc, DomainError):
        return HttpResponse(
            status_code=400,
            body={"detail": str(exc), "error_code": "DOMAIN_ERROR"},
        )

    return HttpResponse(
        status_code=500,
        body={"detail": "Erro interno inesperado no servidor.", "error_code": "INTERNAL_ERROR"},
    )
