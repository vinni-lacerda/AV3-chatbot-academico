"""Contratos HTTP agnósticos a frameworks web (Flask, FastAPI, Django, etc.).

Nenhum controller importa objetos do Flask diretamente.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class HttpRequest:
    """Representação agnóstica de uma requisição HTTP."""

    body: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    path_params: dict[str, str] = field(default_factory=dict)

    def get_header(self, name: str) -> str | None:
        """Busca um header de forma case-insensitive."""
        target = name.lower()
        for key, value in self.headers.items():
            if key.lower() == target:
                return value
        return None


@dataclass(frozen=True)
class HttpResponse:
    """Representação agnóstica de uma resposta HTTP."""

    status_code: int
    body: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)


class IController(ABC):
    """Contrato único para todos os controllers HTTP (SRP & DIP)."""

    @abstractmethod
    def handle(self, request: HttpRequest) -> HttpResponse:
        """Processa um HttpRequest agnóstico e retorna um HttpResponse agnóstico."""
