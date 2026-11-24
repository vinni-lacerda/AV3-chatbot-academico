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
    devo gente tem ha existe quanto organizar sao proxima proximo voce voces
    dao dar faco cada""".split()
)
SYNONYMS = {
    "reenvio": "reenviar",
    "mandar": "reenviar",
    "enviar": "reenviar",
    "planilhas": "planilha",
    "tabela": "planilha",
    "tabelas": "planilha",
    "cartao": "cartoes",
    "ficha": "cartoes",
    "fichas": "cartoes",
    "confirmacoes": "confirmacao",
    "comprovante": "confirmacao",
    "comprovantes": "confirmacao",
    "atraso": "atrasar",
    "atrasos": "atrasar",
    "atrasam": "atrasar",
    "atrasada": "atrasar",
    "atrasadas": "atrasar",
    "demora": "atrasar",
    "demoram": "atrasar",
    "demorar": "atrasar",
    "ocorre": "podem",
    "ocorrem": "podem",
    "ocorrer": "podem",
    "notificacao": "notificacoes",
    "aviso": "notificacoes",
    "avisos": "notificacoes",
    "alerta": "notificacoes",
    "alertas": "notificacoes",
    "duplicada": "duplicatas",
    "duplicadas": "duplicatas",
    "duplicidade": "duplicatas",
    "duplicidades": "duplicatas",
    "repetida": "duplicatas",
    "repetidas": "duplicatas",
    "formularios": "formulario",
    "inscricao": "inscricoes",
    "cadastro": "inscricoes",
    "cadastros": "inscricoes",
    "mensagens": "mensagem",
    "email": "entrada",
    "emails": "entrada",
}
SUFFIXES = (
    "amentos", "imentos", "amento", "imento", "acoes", "icoes", "acao", "icao",
    "adoras", "adores", "adora", "ador", "aveis", "iveis", "avel", "ivel",
    "amos", "emos", "imos", "ando", "endo", "indo", "aram", "eram", "iram",
    "arao", "erao", "irao", "adas", "ados", "idas", "idos", "ada", "ado",
    "ida", "ido", "ares", "eres", "ires", "am", "em", "ar", "er", "ir",
    "oes", "ais", "eis", "ois", "ns", "es", "is", "os", "as", "s", "a", "e", "o",
)


def stem(token: str) -> str:
    token = SYNONYMS.get(token, token)
    if token.isdigit() or len(token) <= 3:
        return token
    for suffix in SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            token = token[: -len(suffix)]
            break
    return token


def normalize_tokens(items: set[str] | frozenset[str]) -> set[str]:
    result = set(items)
    for item in items:
        mapped = SYNONYMS.get(item, item)
        result.add(mapped)
        result.add(stem(item))
    return result


RAW_TOPICS = {
    "etapas": {
        "etapa", "etapas", "passo", "passos", "primeiro", "primeira",
        "inicio", "iniciar", "comeco", "comecar", "procedimento", "procedimentos",
        "roteiro", "ordem", "sequencia", "inicial",
    },
    "recursos": {
        "recurso", "recursos", "ferramenta", "ferramentas", "material", "materiais",
        "acesso", "acessos", "sistema", "sistemas", "documento", "documentos",
    },
    "dificuldades": {
        "dificuldade", "dificuldades", "problema", "problemas", "erro", "erros",
        "falha", "falhas", "obstaculo", "obstaculos", "imprevisto", "imprevistos",
    },
    "solucoes": {
        "solucao", "solucoes", "resolver", "resolvo", "evitar", "corrigir",
        "correcao", "contornar", "saida", "tratamento",
    },
    "decisoes": {
        "decisao", "decisoes", "decidir", "decidimos", "escolha", "escolhas",
        "motivo", "motivos", "criterio", "criterios", "definicao",
    },
    "recomendacoes": {
        "recomendacao", "recomendacoes", "recomenda", "dica", "dicas", "conferir",
        "orientacao", "orientacoes", "conselho", "conselhos", "cuidado", "cuidados",
    },
}
TOPICS = {key: normalize_tokens(aliases) for key, aliases in RAW_TOPICS.items()}


def words(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    raw = set(re.findall(r"[a-z0-9]+", plain)) - STOP_WORDS
    return normalize_tokens(raw)


def raw_words(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    plain = "".join(char for char in normalized if not unicodedata.combining(char))
    return set(re.findall(r"[a-z0-9]+", plain)) - STOP_WORDS


def terms_match(required: set[str], evidence: set[str]) -> tuple[bool, int]:
    if not required:
        return True, 0
    canonical_groups = {stem(term) for term in required}
    matched = sum(1 for group in canonical_groups if group in evidence)
    if matched == len(canonical_groups):
        return True, matched
    if len(canonical_groups) >= 2 and matched >= len(canonical_groups) - 1:
        return True, matched
    return False, matched


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
        terms = raw_words(question)
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
        expanded_terms = normalize_tokens(terms)
        matches = []
        for activity in self.knowledge.activities():
            named = raw_words(activity["title"])
            if not named:
                continue
            ok, score = terms_match(named, expanded_terms)
            if ok:
                matches.append((score, activity))
        matches.sort(key=lambda match: match[0], reverse=True)
        if matches and (len(matches) == 1 or matches[0][0] > matches[1][0]):
            return matches[0][1]
        if not matches and previous:
            return self.knowledge.activity(previous)
        return None

    def retrieve(self, terms: set[str], activity: dict | None) -> list[dict]:
        activity_terms = words(activity["title"]) if activity else set()
        focus = {term for term in terms if term not in activity_terms and stem(term) not in activity_terms}
        expanded_focus = normalize_tokens(focus)
        topics = {key for key, aliases in TOPICS.items() if expanded_focus & aliases}
        topic_tokens = set().union(*(TOPICS[key] for key in topics)) if topics else set()
        details = {term for term in focus if term not in topic_tokens and stem(term) not in topic_tokens}
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
                    if not excerpt:
                        continue
                    excerpt_words = words(excerpt)
                    evidence = excerpt_words | (words(title) if key is None else set())
                    has_topic = key in topics or any(evidence & TOPICS[topic] for topic in topics)
                    ok, matched_count = terms_match(details, evidence)
                    if not ok or (topics and not has_topic):
                        continue
                    _, excerpt_score = terms_match(details, excerpt_words)
                    topic_bonus = 1 if (key in topics) else 0
                    matches.append((matched_count * 10 + excerpt_score + topic_bonus, {
                        "record_id": record["_id"], "version": version["number"],
                        "activity_id": item["id"], "activity": item["title"], "title": title,
                        "author": record["author"]["name"],
                        "origin": content["origin"] if key is None else "Entrevista",
                        "date": content["date"] if key is None else version["submitted_at"][:10],
                        "excerpt": excerpt,
                    }))
        matches.sort(key=lambda match: match[0], reverse=True)
        return [source for _, source in matches[:6]]
