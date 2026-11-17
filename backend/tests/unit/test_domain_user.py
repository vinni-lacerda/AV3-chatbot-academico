"""Testes unitários da entidade User e regras de permissão de domínio (RF01)."""

import pytest

from domain.entities.user import User, UserRole
from domain.exceptions.domain_exceptions import ValidationError


def test_user_creation_normalizes_name_and_email() -> None:
    """Deve remover espaços extras do nome e normalizar o e-mail para minúsculas."""
    user = User(
        name="  Vinicius Lacerda  ",
        email="  Vinicius.Lacerda@Universidade.EDU.BR ",
        password_hash="hashed_secret",
        roles={UserRole.INTEGRANTE},
        academic_id="12725210686",
    )

    assert user.name == "Vinicius Lacerda"
    assert user.email == "vinicius.lacerda@universidade.edu.br"
    assert user.academic_id == "12725210686"
    assert user.is_active is True


def test_user_validation_rejects_short_name() -> None:
    """Deve rejeitar nomes com menos de 2 caracteres úteis."""
    with pytest.raises(ValidationError):
        User(
            name=" A ",
            email="valido@universidade.edu.br",
            password_hash="hashed_secret",
        )


@pytest.mark.parametrize(
    "invalid_email",
    [
        "sem-arroba.com",
        "sem-ponto@dominio",
        "vazio@",
        "",
    ],
)
def test_user_validation_rejects_invalid_email(invalid_email: str) -> None:
    """Deve rejeitar formatos de e-mail inválidos."""
    with pytest.raises(ValidationError):
        User(
            name="Nome Valido",
            email=invalid_email,
            password_hash="hashed_secret",
        )


def test_user_validation_rejects_empty_password_hash() -> None:
    """Deve rejeitar usuário sem hash de senha."""
    with pytest.raises(ValidationError):
        User(
            name="Nome Valido",
            email="valido@universidade.edu.br",
            password_hash="",
        )


def test_user_validation_rejects_empty_roles() -> None:
    """Deve exigir pelo menos um perfil de acesso (RF01)."""
    with pytest.raises(ValidationError):
        User(
            name="Nome Valido",
            email="valido@universidade.edu.br",
            password_hash="hashed_secret",
            roles=set(),
        )


def test_user_permissions_by_role() -> None:
    """Deve calcular corretamente as permissões conforme os perfis do RF01."""
    novo = User(
        name="Novato",
        email="novato@uni.edu.br",
        password_hash="hash",
        roles={UserRole.NOVO_INTEGRANTE},
    )
    assert novo.can_query_knowledge() is True
    assert novo.can_record_knowledge() is False
    assert novo.can_review_knowledge() is False

    integrante = User(
        name="Veterano",
        email="veterano@uni.edu.br",
        password_hash="hash",
        roles={UserRole.INTEGRANTE},
    )
    assert integrante.can_query_knowledge() is True
    assert integrante.can_record_knowledge() is True
    assert integrante.can_review_knowledge() is False

    responsavel = User(
        name="Coordenador",
        email="coord@uni.edu.br",
        password_hash="hash",
        roles={UserRole.RESPONSAVEL},
    )
    assert responsavel.can_query_knowledge() is True
    assert responsavel.can_record_knowledge() is True
    assert responsavel.can_review_knowledge() is True


def test_inactive_user_has_no_permissions() -> None:
    """Usuário inativo não deve possuir nenhuma permissão ativa."""
    inactive_admin = User(
        name="Inativo",
        email="inativo@uni.edu.br",
        password_hash="hash",
        roles={UserRole.INTEGRANTE, UserRole.RESPONSAVEL, UserRole.NOVO_INTEGRANTE},
        is_active=False,
    )

    assert inactive_admin.can_query_knowledge() is False
    assert inactive_admin.can_record_knowledge() is False
    assert inactive_admin.can_review_knowledge() is False
