"""Gerenciador de conexão com o MongoDB (PyMongo isolado na camada de infraestrutura)."""

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

from infrastructure.config.settings import Settings


class MongoDBConnectionManager:
    """Gerencia o ciclo de vida do cliente MongoDB e garante a criação de índices."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: MongoClient | None = None
        self._db: Database | None = None

    def connect(self) -> None:
        """Inicializa o cliente MongoDB e cria índices únicos necessários."""
        self._client = MongoClient(self._settings.mongodb_uri)
        self._db = self._client[self._settings.mongodb_db_name]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        if self._db is None:
            return
        users_col = self._db["users"]
        users_col.create_index([("email", ASCENDING)], unique=True)
        users_col.create_index([("id", ASCENDING)], unique=True)

    def disconnect(self) -> None:
        """Encerra a conexão com o MongoDB."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None

    @property
    def database(self) -> Database:
        if self._db is None:
            self.connect()
        assert self._db is not None
        return self._db
