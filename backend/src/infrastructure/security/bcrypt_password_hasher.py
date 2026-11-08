"""Implementação concreta de hashing de senhas com Bcrypt (LSP & DIP)."""

import bcrypt

from domain.services.password_hasher import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """Adaptador de criptografia de senhas usando o algoritmo bcrypt."""

    def __init__(self, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, plain_password: str) -> str:
        salt = bcrypt.gensalt(rounds=self._rounds)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify(self, plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                password_hash.encode("utf-8"),
            )
        except ValueError:
            return False
