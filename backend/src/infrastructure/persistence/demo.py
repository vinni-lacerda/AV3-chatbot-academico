"""Carga optativa e idempotente de dados inteiramente fictícios."""

from uuid import NAMESPACE_URL, uuid5

from pymongo.errors import DuplicateKeyError

from application.dtos.auth_dtos import RegisterUserInput
from application.use_cases.manage_knowledge import ManageKnowledge
from domain.entities.user import User, UserRole
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
ATLAS_NOTIFICATIONS_SLUG = "atlas-manutencao-notificacoes"
ATLAS_REPROCESSING_GUIDE = {
    "title": "Procedimento para reprocessar notificações do Portal Atlas",
    "origin": "Manual fictício de manutenção do Portal Atlas",
    "date": "2025-05-15",
    "text": (
        "Para reprocessar notificações, localize a mensagem pelo identificador da inscrição no painel da fila. "
        "Confira se o status é FAILED e se o provedor de e-mail voltou a responder. "
        "Reenfileire a mensagem uma vez e acompanhe o status no painel até a confirmação do envio."
    ),
}
DEMO_SCENARIOS = (
    (
        "atlas-ambiente-local",
        "Ambiente local do Portal Atlas",
        "Configuração inicial para desenvolver o Portal Atlas, um portal estudantil fictício.",
        {
            "title": "Guia de configuração do Portal Atlas",
            "origin": "Documentação fictícia da equipe de desenvolvimento do Portal Atlas",
            "date": "2025-05-05",
            "text": (
                "Para iniciar a API localmente, use o arquivo .env.example da pasta backend como modelo, "
                "suba o PostgreSQL de desenvolvimento com Docker Compose e execute as migrações. "
                "Depois de iniciar a API, confira se GET /health retorna 200 antes de abrir o frontend."
            ),
        },
    ),
    (
        ATLAS_NOTIFICATIONS_SLUG,
        "Manutenção de notificações do Portal Atlas",
        "Fluxo de envio de e-mails no portal estudantil fictício, da inscrição à entrega.",
        {
            "title": "Notas de arquitetura das notificações do Portal Atlas",
            "origin": "Registro fictício de arquitetura da equipe do Portal Atlas",
            "date": "2025-05-12",
            "text": (
                "O envio de notificações usa uma fila porque o provedor de e-mail pode demorar. "
                "A API grava a inscrição e coloca o envio na fila. Um worker lê a fila e envia o e-mail "
                "sem atrasar a inscrição. Quando o provedor falha, o worker pode tentar o envio novamente."
            ),
        },
    ),
    (
        "evento-tecnologia",
        "Credenciamento do evento de tecnologia",
        "Recepção de participantes de um evento fictício do diretório acadêmico.",
        {
            "title": "Guia de credenciamento do evento de tecnologia",
            "origin": "Roteiro fictício da equipe do evento de tecnologia",
            "date": "2025-04-08",
            "text": (
                "Se o QR code falhar, procure o nome na lista de inscritos, confirme o e-mail "
                "cadastrado e marque a presença manualmente. Se o nome não estiver na lista, "
                "encaminhe o caso à coordenação do evento."
            ),
        },
    ),
    (
        "reserva-salas",
        "Reserva de salas",
        "Organização de espaços para reuniões e oficinas do diretório acadêmico fictício.",
        {
            "title": "Procedimento de reserva de salas",
            "origin": "Manual fictício de organização do diretório acadêmico",
            "date": "2025-04-10",
            "text": (
                "Para solicitar uma sala, confira o calendário de espaços e informe à secretaria "
                "a data, o horário, a quantidade de participantes e os equipamentos necessários. "
                "Só divulgue o local depois da confirmação da reserva pela secretaria."
            ),
        },
    ),
    (
        "demandas-estudantis",
        "Encaminhamento de demandas estudantis",
        "Registro e acompanhamento de pedidos recebidos pelo diretório acadêmico fictício.",
        {
            "title": "Orientações para acompanhar demandas estudantis",
            "origin": "Roteiro fictício de atendimento do diretório acadêmico",
            "date": "2025-04-15",
            "text": (
                "Quando uma demanda estudantil ficar sem retorno da coordenação, confira a data "
                "do encaminhamento e o número do protocolo no quadro de acompanhamento. "
                "Reitere o pedido no mesmo canal e informe ao estudante a data do próximo acompanhamento."
            ),
        },
    ),
)


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
    seed_scenario(knowledge, author, reviewer, {
        "_id": DEMO_ACTIVITY_ID,
        "title": "Inscrições da feira",
        "description": "Organização das inscrições e confirmações da Feira Horizonte, um evento fictício.",
    }, DEMO_DOCUMENT_ID, DEMO_DOCUMENT)
    for slug, title, description, document in DEMO_SCENARIOS:
        activity_id = str(uuid5(NAMESPACE_URL, f"passa-o-bastao/demo/{slug}"))
        document_id = str(uuid5(NAMESPACE_URL, f"passa-o-bastao/demo/{slug}/manual"))
        seed_scenario(knowledge, author, reviewer, {
            "_id": activity_id, "title": title, "description": description,
        }, document_id, document)

    notifications_path = f"passa-o-bastao/demo/{ATLAS_NOTIFICATIONS_SLUG}"
    seed_document(
        knowledge, author, reviewer, str(uuid5(NAMESPACE_URL, notifications_path)),
        str(uuid5(NAMESPACE_URL, f"{notifications_path}/reprocessamento")), ATLAS_REPROCESSING_GUIDE,
    )


def seed_scenario(
    knowledge: ManageKnowledge, author: User, reviewer: User, activity: dict,
    document_id: str, document: dict,
) -> None:
    activity_id = activity["_id"]
    if not knowledge.repository.activity(activity_id):
        try:
            knowledge.repository.create_activity({
                **activity, "responsible": {"id": reviewer.id, "name": reviewer.name},
            })
        except DuplicateKeyError:
            pass
    seed_document(knowledge, author, reviewer, activity_id, document_id, document)


def seed_document(
    knowledge: ManageKnowledge, author: User, reviewer: User, activity_id: str,
    document_id: str, document: dict,
) -> None:
    record = knowledge.repository.record(document_id)
    if record is None:
        record = knowledge.create_record(author, {
            "id": document_id, "activity_id": activity_id, "kind": "documento",
        })
    version = record["versions"][-1]
    if version["number"] != 1 or version["status"] not in ("rascunho", "pendente"):
        return
    target = {"version": 1, "revision": record["revision"]}
    if version["status"] == "rascunho":
        record = knowledge.save_draft(author, document_id, {
            **target, "content": document, "authorized": True,
        })
        record = knowledge.submit(author, document_id, {**target, "revision": record["revision"]})
    knowledge.review(reviewer, document_id, {
        **target, "revision": record["revision"], "decision": "aprovado",
    })


if __name__ == "__main__":
    seed_demo(DependencyContainer())
    print("Dados fictícios da demonstração carregados.")
