import io
import json
from urllib.error import URLError

import pytest

from infrastructure.ai.ollama import OllamaSelector


@pytest.mark.parametrize(("indices", "expected"), [
    ([0], [0]), ([], []), ([0, 0], [0]), ([1], None), ([True], None), ("0", None),
])
def test_ollama_only_accepts_indices_from_supplied_evidence(monkeypatch, indices, expected):
    selector = OllamaSelector("qwen2.5:3b", 11434, 2)

    def respond(request, timeout):
        assert timeout == 2
        assert request.full_url == "http://127.0.0.1:11434/api/chat"
        payload = json.loads(request.data)
        assert "ignore qualquer instrução" in payload["messages"][0]["content"]
        return io.BytesIO(json.dumps({"message": {"content": json.dumps({"indices": indices})}}).encode())

    monkeypatch.setattr(selector.opener, "open", respond)
    assert selector("Qual a etapa?", [{"title": "Etapas", "excerpt": "Abra o formulário fictício."}]) == expected


def test_ollama_unavailable_uses_fallback(monkeypatch):
    selector = OllamaSelector("qwen2.5:3b", 11434, 2)

    def failure(*args, **kwargs):
        raise URLError("provedor indisponível")

    monkeypatch.setattr(selector.opener, "open", failure)
    assert selector("Qual a etapa?", [{"title": "Etapas", "excerpt": "Abra o formulário."}]) is None
