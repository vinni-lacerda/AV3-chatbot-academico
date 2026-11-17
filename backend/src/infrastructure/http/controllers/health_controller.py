"""Controller HTTP agnóstico para verificação de saúde da API."""

from infrastructure.http.contracts import HttpRequest, HttpResponse, IController


class HealthController(IController):
    """Retorna o status operacional do serviço sem acoplamento ao framework web."""

    def handle(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse(
            status_code=200,
            body={"status": "ok", "service": "passa-o-bastao-backend"},
        )
