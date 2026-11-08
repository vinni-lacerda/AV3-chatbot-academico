"""Testes unitários dos adaptadores de segurança, configuração e repositórios."""

from pathlib import Path
from typing import Any

import jwt
from pymongo.errors import DuplicateKeyError
import pytest

from domain.entities.user import User, UserRole
from domain.exceptions.domain_exceptions import (
    InvalidTokenError,
    UserAlreadyExistsError,
)
from infrastructure.config.settings import _load_dotenv_file, get_settings
from infrastructure.persistence.memory.in_memory_user_repository import (
    InMemoryUserRepository,
)
from infrastructure.persistence.mongodb.repositories.mongo_user_repository import (
    MongoUserRepository,
)
from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from infrastructure.security.jwt_token_provider import JwtTokenProvider


def test_bcrypt_password_hasher_hash_and_verify() -> None:
    """Deve gerar hash irreversível e validar senha correta, incorreta ou hash corrompido."""
    hasher = BcryptPasswordHasher(rounds=4)
    hashed = hasher.hash("MinhaSenhaForte123")

    assert hashed != "MinhaSenhaForte123"
    assert hasher.verify("MinhaSenhaForte123", hashed) is True
    assert hasher.verify("SenhaErrada", hashed) is False
    assert hasher.verify("MinhaSenhaForte123", "hash-invalido-nao-bcrypt") is False


def test_jwt_token_provider_create_and_decode() -> None:
    """Deve emitir e decodificar corretamente um token JWT válido."""
    provider = JwtTokenProvider(
        secret_key="chave-secreta-de-teste-com-32-bytes-minimo",
        algorithm="HS256",
        expire_minutes=15,
    )
    token = provider.create_access_token(
        user_id="user-123",
        email="leoni@uni.edu.br",
        roles=[UserRole.INTEGRANTE, UserRole.RESPONSAVEL],
    )

    payload = provider.decode_access_token(token)
    assert payload.subject == "user-123"
    assert payload.email == "leoni@uni.edu.br"
    assert payload.roles == [UserRole.INTEGRANTE, UserRole.RESPONSAVEL]


def test_jwt_token_provider_expired_token_raises_error() -> None:
    """Deve lançar InvalidTokenError quando o token estiver expirado."""
    provider = JwtTokenProvider(
        secret_key="chave-secreta-de-teste-com-32-bytes-minimo",
        algorithm="HS256",
        expire_minutes=-5,
    )
    expired_token = provider.create_access_token(
        user_id="user-123",
        email="leoni@uni.edu.br",
        roles=[UserRole.NOVO_INTEGRANTE],
    )

    with pytest.raises(InvalidTokenError, match="expirado"):
        provider.decode_access_token(expired_token)


def test_jwt_token_provider_incomplete_payload_raises_error() -> None:
    """Deve lançar InvalidTokenError quando faltarem claims obrigatórias."""
    secret = "chave-secreta-de-teste-com-32-bytes-minimo"
    provider = JwtTokenProvider(secret_key=secret)
    token_without_email = jwt.encode({"sub": "user-123"}, secret, algorithm="HS256")

    with pytest.raises(InvalidTokenError, match="incompleto"):
        provider.decode_access_token(token_without_email)


def test_in_memory_user_repository_crud_and_uniqueness() -> None:
    """Deve persistir e recuperar usuários por ID e e-mail em memória."""
    repo = InMemoryUserRepository()
    user = User(
        name="Rafael Stolf",
        email="rafael@uni.edu.br",
        password_hash="hashed",
        roles={UserRole.INTEGRANTE},
    )

    repo.create(user)
    assert repo.find_by_id(user.id) == user
    assert repo.find_by_email("RAFAEL@uni.edu.br") == user
    assert repo.find_by_id("inexistente") is None
    assert repo.find_by_email("inexistente@uni.edu.br") is None

    with pytest.raises(UserAlreadyExistsError):
        repo.create(user)


class FakeMongoCollection:
    """Dublê de coleção do PyMongo para testar o mapeamento de MongoUserRepository."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []

    def insert_one(self, document: dict[str, Any]) -> None:
        for existing in self.docs:
            if existing["email"] == document["email"]:
                raise DuplicateKeyError("duplicate email")
        self.docs.append(dict(document))

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for doc in self.docs:
            if all(doc.get(k) == v for k, v in query.items()):
                return dict(doc)
        return None


class FakeMongoDatabase:
    """Dublê de Database do PyMongo."""

    def __init__(self) -> None:
        self.collections: dict[str, FakeMongoCollection] = {
            "users": FakeMongoCollection()
        }

    def __getitem__(self, name: str) -> FakeMongoCollection:
        return self.collections[name]


def test_mongo_user_repository_persistence_and_mapping() -> None:
    """Deve mapear User <-> Documento MongoDB e traduzir DuplicateKeyError."""
    fake_db: Any = FakeMongoDatabase()
    repo = MongoUserRepository(fake_db)

    user = User(
        name="Pedro Murilo",
        email="pedro@uni.edu.br",
        password_hash="hashed_pw",
        roles={UserRole.INTEGRANTE, UserRole.RESPONSAVEL},
        academic_id="122519964",
    )

    repo.create(user)

    found_by_email = repo.find_by_email("PEDRO@uni.edu.br")
    assert found_by_email is not None
    assert found_by_email.id == user.id
    assert found_by_email.roles == {UserRole.INTEGRANTE, UserRole.RESPONSAVEL}
    assert found_by_email.academic_id == "122519964"

    found_by_id = repo.find_by_id(user.id)
    assert found_by_id is not None
    assert found_by_id.email == "pedro@uni.edu.br"

    assert repo.find_by_email("naoexiste@uni.edu.br") is None
    assert repo.find_by_id("id-inexistente") is None

    with pytest.raises(UserAlreadyExistsError):
        repo.create(user)


def test_dotenv_loader_and_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Deve carregar variáveis de um arquivo .env usando apenas Python padrão."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        'CUSTOM_TEST_VAR="valor_carregado"\nLINHA_INVALIDA\n',
        encoding="utf-8",
    )
    monkeypatch.delenv("CUSTOM_TEST_VAR", raising=False)

    _load_dotenv_file(str(env_file))
    settings = get_settings()

    assert settings.app_name
    assert settings.mongodb_db_name
