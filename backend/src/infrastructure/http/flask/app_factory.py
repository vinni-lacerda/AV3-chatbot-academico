"""Factory da aplicação Flask que registra as rotas adaptadas aos controllers agnósticos."""

from flask import Blueprint, Flask, Response, request

from domain.repositories.user_repository import IUserRepository
from infrastructure.container.composition_root import DependencyContainer
from infrastructure.http.controllers.docs_controller import build_swagger_ui_html
from infrastructure.http.flask.adapter import adapt_flask_route


def create_flask_app(
    container: DependencyContainer | None = None,
    user_repository_override: IUserRepository | None = None,
) -> Flask:
    """Cria e configura a instância do Flask na borda de infraestrutura."""
    app_container = container or DependencyContainer(
        user_repository=user_repository_override
    )

    app = Flask(__name__)
    app.config["CONTAINER"] = app_container
    allowed_origins = set(app_container.settings.cors_allowed_origins)

    @app.before_request
    def handle_preflight() -> Response | None:
        if request.method == "OPTIONS":
            return Response(status=204)
        return None

    @app.after_request
    def apply_cors_headers(response: Response) -> Response:
        origin = request.headers.get("Origin")
        if origin and ("*" in allowed_origins or origin in allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = (
                "Authorization, Content-Type"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
        return response

    docs_bp = Blueprint("docs", __name__)
    docs_bp.add_url_rule(
        "/openapi.json",
        endpoint="openapi_spec",
        view_func=adapt_flask_route(app_container.openapi_spec_controller),
        methods=["GET"],
    )

    def swagger_ui_view() -> Response:
        return Response(build_swagger_ui_html("/openapi.json"), mimetype="text/html")

    docs_bp.add_url_rule(
        "/docs",
        endpoint="swagger_ui",
        view_func=swagger_ui_view,
        methods=["GET"],
    )

    health_bp = Blueprint("health", __name__, url_prefix="/api/v1/health")
    health_bp.add_url_rule(
        "",
        endpoint="healthcheck",
        view_func=adapt_flask_route(app_container.health_controller),
        methods=["GET"],
    )

    auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
    auth_bp.add_url_rule(
        "/register",
        endpoint="register",
        view_func=adapt_flask_route(app_container.register_user_controller),
        methods=["POST"],
    )
    auth_bp.add_url_rule(
        "/login",
        endpoint="login",
        view_func=adapt_flask_route(app_container.login_user_controller),
        methods=["POST"],
    )
    auth_bp.add_url_rule(
        "/me",
        endpoint="me",
        view_func=adapt_flask_route(app_container.get_me_controller),
        methods=["GET"],
    )
    auth_bp.add_url_rule(
        "/permissions/review-check",
        endpoint="review_check",
        view_func=adapt_flask_route(
            app_container.verify_review_permission_controller
        ),
        methods=["GET"],
    )

    app.register_blueprint(docs_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)

    return app
