"""Rotas e contratos HTTP do fluxo de conhecimento."""

from collections.abc import Callable

from application.use_cases.consult_knowledge import ConsultKnowledge
from application.use_cases.manage_knowledge import ManageKnowledge
from domain.entities.user import User
from domain.knowledge import QUESTIONS
from infrastructure.http.contracts import HttpRequest, HttpResponse, IController
from infrastructure.http.middlewares.auth_guard import AuthGuard


class KnowledgeController(IController):
    def __init__(self, guard: AuthGuard, action: Callable[[User, HttpRequest], dict], status: int) -> None:
        self.guard = guard
        self.action = action
        self.status = status

    def handle(self, request: HttpRequest) -> HttpResponse:
        user = self.guard.authenticate(request)
        return HttpResponse(self.status, self.action(user, request), {"Cache-Control": "no-store"})


def build_knowledge_routes(guard: AuthGuard, knowledge: ManageKnowledge, consult: ConsultKnowledge):
    def questionnaire(_user: User, _request: HttpRequest) -> dict:
        return {"items": [
            {"key": key, "title": title, "prompt": prompt} for key, title, prompt in QUESTIONS
        ]}

    def record_action(method):
        return lambda user, req: method(user, req.path_params["identifier"], req.body)

    routes = (
        ("GET", "/activities", 200, lambda _user, _req: {"items": knowledge.activities()}),
        ("POST", "/activities", 201, lambda user, req: knowledge.create_activity(user, req.body)),
        ("GET", "/interview/questions", 200, questionnaire),
        ("GET", "/records", 200, lambda user, req: {"items": knowledge.list_records(user, req.query_params)}),
        ("POST", "/records", 201, lambda user, req: knowledge.create_record(user, req.body)),
        ("PUT", "/records/<identifier>/draft", 200, record_action(knowledge.save_draft)),
        ("POST", "/records/<identifier>/submit", 200, record_action(knowledge.submit)),
        ("POST", "/records/<identifier>/revise", 201, record_action(knowledge.revise)),
        ("POST", "/records/<identifier>/review", 200, record_action(knowledge.review)),
        ("GET", "/sources/<identifier>/<int:version>", 200, lambda _user, req: knowledge.approved_source(
            req.path_params["identifier"], int(req.path_params["version"])
        )),
        ("POST", "/chat", 200, lambda _user, req: consult.answer(req.body)),
    )
    for method, path, status, action in routes:
        yield method, path, KnowledgeController(guard, action, status)
