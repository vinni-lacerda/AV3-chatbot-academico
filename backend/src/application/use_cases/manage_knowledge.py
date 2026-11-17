"""Permissões, validação e ciclo de vida dos registros do piloto."""

from copy import deepcopy
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from domain.entities.user import User, UserRole
from domain.exceptions.domain_exceptions import ForbiddenRoleError, ValidationError
from domain.knowledge import KnowledgeConflict, KnowledgeNotFound, QUESTIONS, Status
from domain.repositories.knowledge_repository import KnowledgeRepository
from domain.repositories.user_repository import IUserRepository


def text_field(data: dict, key: str, limit: int, *, required: bool = True) -> str:
    value = data.get(key, "")
    if not isinstance(value, str):
        raise ValidationError(f"O campo '{key}' deve ser um texto.")
    value = value.strip()
    if len(value) > limit or (required and not value):
        raise ValidationError(f"Confira o campo '{key}' (até {limit} caracteres).")
    return value


def iso_date(value: str) -> str:
    try:
        if date.fromisoformat(value).isoformat() == value:
            return value
    except ValueError:
        pass
    raise ValidationError("Informe a data no formato AAAA-MM-DD.")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def identity(user: User) -> dict:
    return {"id": user.id, "name": user.name}


def public_activity(activity: dict) -> dict:
    return {
        "id": activity["_id"],
        "title": activity["title"],
        "description": activity["description"],
        "responsible": activity["responsible"],
    }


class ManageKnowledge:
    def __init__(self, repository: KnowledgeRepository, users: IUserRepository) -> None:
        self.repository = repository
        self.users = users

    def activities(self) -> list[dict]:
        return [public_activity(item) for item in self.repository.activities()]

    def activity(self, identifier: str) -> dict:
        activity = self.repository.activity(identifier)
        if not activity:
            raise KnowledgeNotFound("Atividade não encontrada.")
        return public_activity(activity)

    def create_activity(self, user: User, body: dict) -> dict:
        self.require_reviewer(user)
        responsible_id = text_field(body, "responsible_id", 64)
        responsible = self.users.find_by_id(responsible_id)
        if not responsible or not responsible.can_review_knowledge():
            raise ValidationError("Selecione um responsável ativo cadastrado.")
        activity = {
            "_id": str(uuid4()),
            "title": text_field(body, "title", 120),
            "description": text_field(body, "description", 1000),
            "responsible": identity(responsible),
        }
        self.repository.create_activity(activity)
        return public_activity(activity)

    def require_reviewer(self, user: User) -> None:
        if not user.can_review_knowledge():
            raise ForbiddenRoleError([UserRole.RESPONSAVEL])

    def create_record(self, user: User, body: dict) -> dict:
        if not user.can_record_knowledge():
            raise ForbiddenRoleError([UserRole.INTEGRANTE, UserRole.RESPONSAVEL])
        try:
            identifier = str(UUID(text_field(body, "id", 36)))
        except ValueError as exc:
            raise ValidationError("Informe um identificador UUID para o rascunho.") from exc
        activity_id = self.activity(text_field(body, "activity_id", 64))["id"]
        kind = body.get("kind")
        if kind not in ("entrevista", "documento"):
            raise ValidationError("Selecione entrevista ou documento.")
        now = utc_now()
        record = {
            "_id": identifier, "activity_id": activity_id, "kind": kind,
            "author": identity(user), "created_at": now, "updated_at": now, "revision": 1,
            "versions": [{
                "number": 1, "editor": identity(user), "status": Status.DRAFT.value,
                "created_at": now, "updated_at": now, "content": {}, "authorized": False,
                "reviews": [],
            }],
        }
        if not self.repository.insert_record(record):
            record = self.owned_record(user, identifier)
            if record["activity_id"] != activity_id or record["kind"] != kind:
                raise KnowledgeConflict("Já existe um registro com esse identificador.")
        return self.serialize(record, record["versions"])

    def owned_record(self, user: User, identifier: str) -> dict:
        if not user.can_record_knowledge():
            raise ForbiddenRoleError([UserRole.INTEGRANTE, UserRole.RESPONSAVEL])
        record = self.get_record(identifier)
        if record["author"]["id"] != user.id:
            raise KnowledgeNotFound("Registro não encontrado.")
        return record

    def get_record(self, identifier: str) -> dict:
        record = self.repository.record(identifier)
        if not record:
            raise KnowledgeNotFound("Registro não encontrado.")
        return record

    def serialize(self, record: dict, versions: list[dict]) -> dict:
        return {
            "id": record["_id"], "activity_id": record["activity_id"], "kind": record["kind"],
            "author": record["author"], "created_at": record["created_at"],
            "updated_at": versions[-1]["updated_at"], "revision": record["revision"],
            "versions": versions,
        }

    @staticmethod
    def public_version(version: dict) -> dict:
        return {key: value for key, value in version.items() if key != "reviews"}

    def list_records(self, user: User, filters: dict) -> list[dict]:
        view = filters.get("view", "library")
        if view not in ("library", "mine", "review"):
            raise ValidationError("Visualização inválida.")
        if view == "review":
            self.require_reviewer(user)

        query = {}
        if activity_id := filters.get("activity_id"):
            self.activity(activity_id)
            query["activity_id"] = activity_id
        if view == "mine":
            query["author.id"] = user.id
        if since := filters.get("since"):
            iso_date(since)
        status = filters.get("status")
        if status and status not in set(Status):
            raise ValidationError("Situação inválida.")

        result = []
        for record in self.repository.records(query):
            if record["author"]["id"] == user.id:
                versions = record["versions"]
            elif user.can_review_knowledge():
                versions = [version for version in record["versions"] if version["status"] != Status.DRAFT]
            else:
                versions = [self.public_version(version) for version in record["versions"] if self.visible(version)]
            if not versions:
                continue
            if not any(
                (not status or version["status"] == status)
                and (not since or version["updated_at"][:10] >= since)
                for version in versions
            ):
                continue
            entry = self.serialize(record, versions)
            if record["author"]["id"] != user.id and not user.can_review_knowledge():
                entry.pop("revision")
            result.append(entry)
        return sorted(result, key=lambda item: item["updated_at"], reverse=True)

    @staticmethod
    def visible(version: dict) -> bool:
        return version["status"] == Status.APPROVED and version["authorized"] is True

    def save_draft(self, user: User, identifier: str, body: dict) -> dict:
        record = self.owned_record(user, identifier)
        version = self.target(record, body)
        if version is not record["versions"][-1] or version["status"] != Status.DRAFT:
            raise KnowledgeConflict("A versão já saiu do rascunho.")
        content = self.content(record["kind"], body.get("content"))
        authorized = body.get("authorized", False)
        if type(authorized) is not bool:
            raise ValidationError("Confirme a autorização de uso.")
        if version["content"] != content or version["authorized"] != authorized:
            self.check_revision(record, body)
            version.update(content=content, authorized=authorized, updated_at=utc_now())
            self.persist(record)
        return self.serialize(record, record["versions"])

    def submit(self, user: User, identifier: str, body: dict) -> dict:
        record = self.owned_record(user, identifier)
        version = self.target(record, body)
        if "submitted_at" in version:
            return self.serialize(record, record["versions"])
        self.check_revision(record, body)
        if version is not record["versions"][-1] or version["status"] != Status.DRAFT:
            raise KnowledgeConflict("A versão já saiu do rascunho.")
        self.content(record["kind"], version["content"], required=True)
        if not version["authorized"]:
            raise ValidationError("Confirme a autorização de uso antes de enviar.")
        now = utc_now()
        version.update(status=Status.PENDING.value, submitted_at=now, updated_at=now)
        self.persist(record)
        return self.serialize(record, record["versions"])

    def revise(self, user: User, identifier: str, body: dict) -> dict:
        record = self.owned_record(user, identifier)
        base = self.target(record, body)
        latest = record["versions"][-1]
        if latest["status"] == Status.DRAFT and latest.get("based_on") == base["number"]:
            return self.serialize(record, record["versions"])
        self.check_revision(record, body)
        if base is not latest or latest["status"] not in (Status.APPROVED, Status.CHANGES, Status.WITHDRAWN):
            raise KnowledgeConflict("A versão mais recente deve ser revisada antes de iniciar outra.")
        if latest["number"] >= 100:
            raise KnowledgeConflict("O registro atingiu 100 versões. Crie um novo registro para continuar.")
        now = utc_now()
        record["versions"].append({
            "number": latest["number"] + 1, "based_on": latest["number"], "editor": identity(user),
            "created_at": now, "updated_at": now, "status": Status.DRAFT.value,
            "content": deepcopy(latest["content"]), "authorized": False, "reviews": [],
        })
        self.persist(record)
        return self.serialize(record, record["versions"])

    def review(self, user: User, identifier: str, body: dict) -> dict:
        self.require_reviewer(user)
        record = self.get_record(identifier)
        self.check_revision(record, body)
        version = self.target(record, body)
        decision = body.get("decision")
        if decision not in (Status.APPROVED, Status.CHANGES, Status.WITHDRAWN):
            raise ValidationError("Decisão de revisão inválida.")
        note = text_field(body, "note", 1500, required=decision == Status.CHANGES)
        expected = Status.APPROVED if decision == Status.WITHDRAWN else Status.PENDING
        if version["status"] != expected or not version["authorized"]:
            raise KnowledgeConflict("A situação atual não permite essa decisão.")

        now = utc_now()
        if decision == Status.APPROVED:
            for previous in record["versions"]:
                if previous["status"] == Status.APPROVED:
                    previous.update(status=Status.SUPERSEDED.value, updated_at=now)
        version.update(status=decision, updated_at=now)
        version["reviews"].append({"reviewer": identity(user), "decision": decision, "note": note, "date": now})
        self.persist(record)
        versions = [
            item for item in record["versions"]
            if item["status"] != Status.DRAFT or record["author"]["id"] == user.id
        ]
        return self.serialize(record, versions)

    def approved_source(self, identifier: str, number: int) -> dict:
        record = self.get_record(identifier)
        version = self.target(record, {"version": number})
        if not self.visible(version):
            raise KnowledgeNotFound("Fonte não disponível para consulta.")
        source = self.serialize(record, [self.public_version(version)])
        source.pop("revision")
        return source

    @staticmethod
    def content(kind: str, value: object, *, required: bool = False) -> dict:
        if not isinstance(value, dict):
            raise ValidationError("Confira os campos do conteúdo.")
        if kind == "entrevista":
            return {key: text_field(value, key, 1500, required=required) for key, _, _ in QUESTIONS}
        fields = {"title": 160, "origin": 350, "date": 10, "text": 8000}
        content = {key: text_field(value, key, limit, required=required) for key, limit in fields.items()}
        if content["date"]:
            iso_date(content["date"])
        return content

    @staticmethod
    def target(record: dict, body: dict) -> dict:
        number = body.get("version")
        if type(number) is not int or not 1 <= number <= len(record["versions"]):
            raise KnowledgeNotFound("Versão não encontrada.")
        return record["versions"][number - 1]

    @staticmethod
    def check_revision(record: dict, body: dict) -> None:
        if type(body.get("revision")) is not int or body["revision"] != record["revision"]:
            raise KnowledgeConflict("O registro mudou. Atualize a página antes de continuar.")

    def persist(self, record: dict) -> None:
        previous = record["revision"]
        record["revision"] += 1
        record["updated_at"] = utc_now()
        if not self.repository.replace_record(record, previous):
            raise KnowledgeConflict("O registro mudou. Atualize a página antes de continuar.")
