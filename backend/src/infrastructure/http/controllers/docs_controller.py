"""Controllers agnósticos para exposição da especificação OpenAPI e interface Swagger UI."""

from infrastructure.http.contracts import HttpRequest, HttpResponse, IController
from infrastructure.http.openapi_spec import build_openapi_spec


class OpenApiSpecController(IController):
    """Retorna o JSON da especificação OpenAPI 3.0.3 sem depender de bibliotecas externas."""

    def handle(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse(status_code=200, body=build_openapi_spec())


def build_swagger_ui_html(openapi_url: str = "/openapi.json") -> str:
    """Gera o HTML da interface interativa Swagger UI apontando para a especificação da API."""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Passa o Bastão API — Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
  <style>
    body {{ margin: 0; background: #fafafa; }}
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
  <script>
    window.onload = function() {{
      window.ui = SwaggerUIBundle({{
        url: "{openapi_url}",
        dom_id: "#swagger-ui",
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis
        ],
        persistAuthorization: true
      }});
    }};
  </script>
</body>
</html>"""
