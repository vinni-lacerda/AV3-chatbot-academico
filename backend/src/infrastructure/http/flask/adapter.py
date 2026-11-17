"""Adaptador de rotas do Flask para o contrato IController agnóstico (Clean Architecture).

Isola completamente o Flask na borda mais externa da aplicação.
"""

from collections.abc import Callable
from typing import Any

from flask import Response, jsonify, make_response, request

from infrastructure.http.contracts import HttpRequest, HttpResponse, IController
from infrastructure.http.error_mapper import map_domain_error_to_http_response


def adapt_flask_route(controller: IController) -> Callable[..., Response]:
    """Transforma um IController puro em uma view function compatível com o Flask."""

    def flask_view(**view_args: Any) -> Response:
        body: dict[str, Any] = {}
        if request.is_json:
            parsed = request.get_json(silent=True)
            if isinstance(parsed, dict):
                body = parsed

        http_request = HttpRequest(
            body=body,
            headers={k: v for k, v in request.headers.items()},
            query_params={k: v for k, v in request.args.items()},
            path_params={k: str(v) for k, v in view_args.items()},
        )

        try:
            http_response: HttpResponse = controller.handle(http_request)
        except Exception as exc:
            http_response = map_domain_error_to_http_response(exc)

        response = make_response(
            jsonify(http_response.body),
            http_response.status_code,
        )
        for header_name, header_value in http_response.headers.items():
            response.headers[header_name] = header_value

        return response

    return flask_view
