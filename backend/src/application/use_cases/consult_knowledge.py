"""Consulta extrativa sobre versões aprovadas, com seleção opcional por IA."""

import re
import unicodedata
from collections.abc import Callable, Iterator

from application.use_cases.manage_knowledge import ManageKnowledge, text_field
from domain.knowledge import KnowledgeNotFound, QUESTIONS, Status

STOP_WORDS = set(
    """a ao aos as o os da das de do dos e em na nas no nos para por com um uma
    me eu se minha meu sobre que qual quais como quando onde quem posso preciso
    vou fazer saber executar assumir atividade projeto funciona isso depois
    devo gente tem ha existe quanto organizar sao proxima proximo""".split()
)
TOPICS = {
    "etapas": {"etapa", "etapas", "passo", "passos", "primeiro", "primeira", "inicio", "iniciar", "comeco", "comecar"},
    "recursos": {"recurso", "recursos", "ferramenta", "ferramentas", "material", "materiais"},
    "dificuldades": {"dificuldade", "dificuldades", "problema", "problemas"},
    "solucoes": {"solucao", "solucoes", "resolver", "resolvo", "evitar"},
    "decisoes": {"decisao", "decisoes", "decidir"},
    "recomendacoes": {"recomendacao", "recomendacoes", "recomenda", "dica", "dicas", "conferir"},
}


def words(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    return set(re.findall(r"[a-z0-9]+", plain)) - STOP_WORDS


def passages(record: dict, version: dict) -> Iterator[tuple[str | None, str, str]]:
    content = version["content"]
    if record["kind"] == "entrevista":
        for key, title, _ in QUESTIONS:
            yield key, title, content[key]
    else:
        for paragraph in re.split(r"\n\s*\n", content["text"]):
            for offset in range(0, len(paragraph), 1500):
                yield None, content["title"], paragraph[offset:offset + 1500].strip()


class ConsultKnowledge:
    def __init__(
        self,
        knowledge: ManageKnowledge,
        select: Callable[[str, list[dict]], list[int] | None] | None = None,
    ) -> None:
        self.knowledge = knowledge
        self.select = select

    def answer(self, body: dict) -> dict:
        question = text_field(body, "question", 500)
        scope = text_field(body, "activity_id", 64, required=False)
        previous = text_field(body, "context_activity_id", 64, required=False)
        terms = words(question)
        activity = self.resolve_activity(terms, scope, previous)
        activity_id = activity["id"] if activity else None
        candidates = self.retrieve(terms, activity)
        mode = "extractive"
        if candidates and self.select:
            selected = self.select(question, candidates)
            if selected is not None:
                candidates = [candidates[index] for index in selected]
                mode = "ollama"

        # Revalida depois da chamada ao modelo, que pode demorar mais que uma revisão humana.
        results = []
        for source in candidates:
            try:
                self.knowledge.approved_source(source["record_id"], source["version"])
            except KnowledgeNotFound:
                continue
            results.append(source)
            if len(results) == 3:
                break
        if not activity and results and len({source["activity_id"] for source in results}) == 1:
            activity_id = results[0]["activity_id"]
        responsible = None
        if not results and activity and activity["responsible"]:
            member = self.knowledge.users.find_by_id(activity["responsible"]["id"])
            if member and member.can_review_knowledge():
                responsible = {"id": member.id, "name": member.name}
        return {
            "answer": (
                "\n\n".join(source["excerpt"] for source in results)
                if results else "Ainda não há informação aprovada suficiente para responder a esta pergunta."
            ),
            "gap": not results,
            "activity_id": activity_id,
            "responsible": responsible,
            "sources": results,
            "mode": mode,
        }

    def resolve_activity(self, terms: set[str], scope: str, previous: str) -> dict | None:
        if scope:
            return self.knowledge.activity(scope)
        matches = [
            (len(named), activity)
            for activity in self.knowledge.activities()
            if (named := words(activity["title"])) and named <= terms
        ]
        matches.sort(key=lambda match: match[0], reverse=True)
        if matches and (len(matches) == 1 or matches[0][0] > matches[1][0]):
            return matches[0][1]
        if not matches and previous:
            return self.knowledge.activity(previous)
        return None

    def retrieve(self, terms: set[str], activity: dict | None) -> list[dict]:
        focus = terms - words(activity["title"]) if activity else terms
        topics = {key for key, aliases in TOPICS.items() if focus & aliases}
        details = focus.difference(*(TOPICS[key] for key in topics))
        if not details and not (topics and activity):
            return []
        query = {"versions.status": Status.APPROVED.value}
        if activity:
            query["activity_id"] = activity["id"]

        matches = []
        activities = {item["id"]: item for item in self.knowledge.activities()}
        for record in self.knowledge.repository.records(query):
            item = activities[record["activity_id"]]
            for version in record["versions"]:
                if not self.knowledge.visible(version):
                    continue
                content = version["content"]
                for key, title, excerpt in passages(record, version):
                    evidence = words(excerpt) | (words(title) if key is None else set())
                    has_topic = key in topics or any(evidence & TOPICS[topic] for topic in topics)
                    if not excerpt or not details <= evidence or (topics and not has_topic):
                        continue
                    matches.append((len(details & words(excerpt)), {
                        "record_id": record["_id"], "version": version["number"],
                        "activity_id": item["id"], "activity": item["title"], "title": title,
                        "author": record["author"]["name"],
                        "origin": content["origin"] if key is None else "Entrevista",
                        "date": content["date"] if key is None else version["submitted_at"][:10],
                        "excerpt": excerpt,
                    }))
        matches.sort(key=lambda match: match[0], reverse=True)
        return [source for _, source in matches[:6]]
