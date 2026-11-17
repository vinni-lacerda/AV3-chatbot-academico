"""Roteiro e estados do fluxo de conhecimento."""

from enum import StrEnum

from domain.exceptions.domain_exceptions import DomainError


class Status(StrEnum):
    DRAFT = "rascunho"
    PENDING = "pendente"
    CHANGES = "ajustes_solicitados"
    APPROVED = "aprovado"
    WITHDRAWN = "retirado"
    SUPERSEDED = "substituido"


QUESTIONS = (
    ("etapas", "Etapas", "Como você executava a atividade, desde o primeiro passo?"),
    ("recursos", "Recursos", "Quais ferramentas, materiais ou acessos eram necessários?"),
    ("dificuldades", "Dificuldades", "Quais dificuldades apareciam com mais frequência?"),
    ("solucoes", "Soluções", "Como você resolvia ou evitava essas dificuldades?"),
    ("decisoes", "Decisões", "Quais decisões foram tomadas e por quê?"),
    ("recomendacoes", "Recomendações", "Que recomendações você daria a quem vai assumir?"),
)


class KnowledgeNotFound(DomainError):
    pass


class KnowledgeConflict(DomainError):
    pass
