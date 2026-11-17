"""Contrato (Port) para hashing e verificação de senhas (ISP & DIP)."""

from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Interface para geração e verificação segura de hash de senha."""

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Transforma uma senha em texto puro em um hash irreversível."""

    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        """Verifica se a senha em texto puro corresponde ao hash armazenado."""
