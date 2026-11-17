"""Ponto de entrada da aplicação backend (Flask na borda externa)."""

from infrastructure.config.settings import get_settings
from infrastructure.http.flask.app_factory import create_flask_app

app = create_flask_app()

if __name__ == "__main__":
    settings = get_settings()
    app.run(host="0.0.0.0", port=8000, debug=settings.debug)
