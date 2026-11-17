"""Contrato de entrada dos endpoints de conhecimento para o Swagger."""

from domain.knowledge import QUESTIONS, Status


def object_schema(properties, required=()):
    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = list(required)
    return schema


def knowledge_paths():
    string = {"type": "string"}
    identifier = {"type": "string", "format": "uuid"}
    positive_integer = {"type": "integer", "minimum": 1}
    date = {"type": "string", "format": "date"}
    target = {"version": positive_integer, "revision": positive_integer}
    interview = object_schema({key: string for key, _, _ in QUESTIONS})
    document = object_schema({"title": string, "origin": string, "date": date, "text": string})

    def parameter(name, location, schema):
        return {"name": name, "in": location, "required": location == "path", "schema": schema}

    record_id = parameter("identifier", "path", identifier)
    source_version = parameter("version", "path", positive_integer)
    record_filters = [
        parameter("view", "query", {"type": "string", "enum": ["library", "mine", "review"]}),
        parameter("activity_id", "query", identifier),
        parameter("status", "query", {"type": "string", "enum": [status.value for status in Status]}),
        parameter("since", "query", date),
    ]
    operations = (
        ("/activities", "get", "Listar atividades", "200", None, []),
        ("/activities", "post", "Cadastrar atividade", "201", object_schema({
            "title": string, "description": string, "responsible_id": identifier,
        }, ("title", "description", "responsible_id")), []),
        ("/activities/{identifier}", "get", "Consultar atividade", "200", None, [record_id]),
        ("/interview/questions", "get", "Listar perguntas da entrevista", "200", None, []),
        ("/records", "get", "Listar registros e versões visíveis", "200", None, record_filters),
        ("/records", "post", "Criar rascunho", "201", object_schema({
            "id": identifier, "activity_id": identifier,
            "kind": {"type": "string", "enum": ["entrevista", "documento"]},
        }, ("id", "activity_id", "kind")), []),
        ("/records/{identifier}/draft", "put", "Salvar rascunho", "200", object_schema({
            **target, "content": {"anyOf": [interview, document]}, "authorized": {"type": "boolean"},
        }, (*target, "content")), [record_id]),
        ("/records/{identifier}/submit", "post", "Enviar para revisão", "200",
         object_schema(target, target), [record_id]),
        ("/records/{identifier}/revise", "post", "Criar nova versão em rascunho", "201",
         object_schema(target, target), [record_id]),
        ("/records/{identifier}/review", "post", "Aprovar, solicitar ajustes ou retirar", "200", object_schema({
            **target, "decision": {"type": "string", "enum": ["aprovado", "ajustes_solicitados", "retirado"]},
            "note": string,
        }, (*target, "decision")), [record_id]),
        ("/sources/{identifier}/{version}", "get", "Inspecionar fonte aprovada", "200", None,
         [record_id, source_version]),
        ("/chat", "post", "Consultar a base aprovada", "200", object_schema({
            "question": {"type": "string", "maxLength": 500}, "activity_id": string,
            "context_activity_id": string,
        }, ("question",)), []),
    )
    paths = {}
    for route, method, summary, success, body, parameters in operations:
        operation = {
            "tags": ["Conhecimento"],
            "summary": summary,
            "security": [{"BearerAuth": []}],
            "responses": {
                success: {"description": "Operação concluída."},
                "401": {"description": "Identificação ausente ou inválida."},
                "default": {
                    "description": "Erro na solicitação.",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}},
                },
            },
        }
        if parameters:
            operation["parameters"] = parameters
        if body:
            operation["requestBody"] = {
                "required": True, "content": {"application/json": {"schema": body}},
            }
        paths.setdefault(f"/api/v1{route}", {})[method] = operation
    return paths
