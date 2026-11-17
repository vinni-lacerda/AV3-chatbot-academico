"""Carga optativa e idempotente de dados inteiramente fictícios."""

from uuid import NAMESPACE_URL, uuid5

from pymongo.errors import DuplicateKeyError

from application.dtos.auth_dtos import RegisterUserInput
from domain.entities.user import UserRole
from domain.exceptions.domain_exceptions import UserAlreadyExistsError
from infrastructure.container.composition_root import DependencyContainer


DEMO_PASSWORD = "Bastao-Demo-2026!"
DEMO_USERS = (
    ("Lia Monteiro · Demo", "lia@demo.example", UserRole.INTEGRANTE),
    ("Beto Alves · Demo", "beto@demo.example", UserRole.RESPONSAVEL),
    ("Ada Wong - Demo", "ada@demo.example", UserRole.NOVO_INTEGRANTE),
)
DEMO_ACTIVITY_ID = str(uuid5(NAMESPACE_URL, "passa-o-bastao/demo/feira"))
DEMO_DOCUMENT_ID = str(uuid5(NAMESPACE_URL, "passa-o-bastao/demo/manual"))
DEMO_DATE = "2025-03-12"
DEMO_DOCUMENT = {
    "title": "Guia de confirmação da feira",
    "origin": "Manual interno fictício da Feira Horizonte",
    "date": DEMO_DATE,
    "text": (
        "Para reenviar uma confirmação, abra a planilha da feira, filtre os cartões pendentes "
        "e use o modelo de mensagem da pasta do evento."
    ),
}


def seed_demo(container: DependencyContainer) -> None:
    knowledge = container.knowledge
    if knowledge is None or container.settings.app_env not in {"development", "test"}:
        raise RuntimeError("Configure um ambiente de desenvolvimento ou teste para carregar a demonstração.")
    users = []
    for name, email, role in DEMO_USERS:
        try:
            container.register_user_use_case.execute(RegisterUserInput(name, email, DEMO_PASSWORD, [role]))
        except UserAlreadyExistsError:
            pass
        user = container.user_repository.find_by_email(email)
        if not user or not user.is_active or user.roles != {role}:
            raise RuntimeError(f"Conta de demonstração incompatível: {email}")
        users.append(user)

    author, reviewer, _ = users
    if not knowledge.repository.activity(DEMO_ACTIVITY_ID):
        activity = {
            "_id": DEMO_ACTIVITY_ID,
            "title": "Inscrições da feira",
            "description": "Organização das inscrições e confirmações da Feira Horizonte, um evento fictício.",
            "responsible": {"id": reviewer.id, "name": reviewer.name},
        }
        try:
            knowledge.repository.create_activity(activity)
        except DuplicateKeyError:
            pass

    if not knowledge.repository.record(DEMO_DOCUMENT_ID):
        record = knowledge.create_record(author, {
            "id": DEMO_DOCUMENT_ID, "activity_id": DEMO_ACTIVITY_ID, "kind": "documento",
        })
    else:
        record = knowledge.repository.record(DEMO_DOCUMENT_ID)
    version = record["versions"][-1]
    if version["number"] != 1 or version["status"] not in ("rascunho", "pendente"):
        return
    target = {"version": 1, "revision": record["revision"]}
    if version["status"] == "rascunho":
        record = knowledge.save_draft(author, DEMO_DOCUMENT_ID, {
            **target, "content": DEMO_DOCUMENT, "authorized": True,
        })
        record = knowledge.submit(author, DEMO_DOCUMENT_ID, {**target, "revision": record["revision"]})
    knowledge.review(reviewer, DEMO_DOCUMENT_ID, {
        **target, "revision": record["revision"], "decision": "aprovado",
    })


if __name__ == "__main__":
    seed_demo(DependencyContainer())
    print("Dados fictícios da demonstração carregados.")
