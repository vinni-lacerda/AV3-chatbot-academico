"""Validação dos documentos gravados no MongoDB."""

from pymongo.database import Database
from pymongo.errors import CollectionInvalid, OperationFailure

from domain.entities.user import UserRole
from domain.knowledge import QUESTIONS, Status


def object_schema(properties: dict, *, optional: tuple[str, ...] = ()) -> dict:
    return {
        "bsonType": "object",
        "required": [field for field in properties if field not in optional],
        "properties": properties,
    }


def text_schema(max_length: int, min_length: int = 0) -> dict:
    return {"bsonType": "string", "minLength": min_length, "maxLength": max_length}


def array_schema(items: dict, **limits) -> dict:
    return {"bsonType": "array", "items": items, **limits}


identifier = {"bsonType": "string", "minLength": 1}
timestamp = {"bsonType": "string", "minLength": 1}
bson_date = {"bsonType": "date"}
positive_int = {"bsonType": ["int", "long"], "minimum": 1}
identity = object_schema({"id": identifier, "name": {"bsonType": "string", "minLength": 2}})
review = object_schema({
    "reviewer": identity,
    "decision": {"enum": [Status.APPROVED.value, Status.CHANGES.value, Status.WITHDRAWN.value]},
    "note": text_schema(1500),
    "date": timestamp,
})


def record_schema(kind: str, fields: dict) -> dict:
    version = object_schema({
        "number": positive_int,
        "based_on": positive_int,
        "editor": identity,
        "status": {"enum": [status.value for status in Status]},
        "created_at": timestamp,
        "updated_at": timestamp,
        "submitted_at": timestamp,
        "content": {"bsonType": "object", "properties": fields, "additionalProperties": False},
        "authorized": {"bsonType": "bool"},
        "reviews": array_schema(review),
    }, optional=("based_on", "submitted_at"))
    return object_schema({
        "_id": identifier,
        "activity_id": identifier,
        "kind": {"enum": [kind]},
        "author": identity,
        "created_at": timestamp,
        "updated_at": timestamp,
        "revision": positive_int,
        "versions": array_schema(version, minItems=1, maxItems=100),
    })


SCHEMAS = {
    "users": object_schema({
        "id": identifier,
        "name": {"bsonType": "string", "minLength": 2},
        "email": {"bsonType": "string", "minLength": 1},
        "password_hash": {"bsonType": "string", "minLength": 1},
        "roles": array_schema({"enum": [role.value for role in UserRole]}, minItems=1, uniqueItems=True),
        "academic_id": {"bsonType": ["string", "null"]},
        "is_active": {"bsonType": "bool"},
        "created_at": bson_date,
        "updated_at": bson_date,
    }, optional=("academic_id",)),
    "activities": object_schema({
        "_id": identifier,
        "title": text_schema(120, 1),
        "description": text_schema(1000, 1),
        "responsible": identity,
    }),
    "knowledge_records": {
        "oneOf": [
            record_schema("entrevista", {key: text_schema(1500) for key, _, _ in QUESTIONS}),
            record_schema("documento", {
                "title": text_schema(160),
                "origin": text_schema(350),
                "date": {"bsonType": "string", "pattern": r"^(?:[0-9]{4}-[0-9]{2}-[0-9]{2})?$"},
                "text": text_schema(8000),
            }),
        ],
    },
}


def ensure_schema(database: Database) -> None:
    """Instala os validadores em bases novas e atualiza os de coleções existentes."""
    for name, schema in SCHEMAS.items():
        options = {
            "validator": {"$jsonSchema": schema},
            "validationLevel": "strict",
            "validationAction": "error",
        }
        collection = next(database.list_collections(filter={"name": name}), None)
        if collection is None:
            try:
                database.create_collection(name, **options)
                continue
            except CollectionInvalid:
                # Outra instância pode ter criado a coleção desde a consulta.
                pass
            except OperationFailure as exc:
                if exc.code != 48:  # NamespaceExists
                    raise
        elif all(collection["options"].get(key) == value for key, value in options.items()):
            continue
        database.command("collMod", name, **options)
