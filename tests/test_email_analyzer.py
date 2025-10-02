import json
import pytest
from services.email_analyzer import EmailAnalyzerService


class FakeGeminiClient:
    def __init__(self, payload: str):
        self._payload = payload

    def generate_json(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1024) -> str:
        assert isinstance(prompt, str) and len(prompt) > 0
        return self._payload


def test_analyze_returns_valid_json_dict():
    payload = json.dumps({
        "atencao_humana": "NÃO",
        "categoria": "Informação Geral",
        "resumo": "Mensagem de boas festas.",
        "sugestao_resposta_ou_acao": "Agradecer cordialmente."
    })
    service = EmailAnalyzerService(client=FakeGeminiClient(payload))
    result = service.analyze("Olá e boas festas!")
    assert isinstance(result, dict)
    assert result["atencao_humana"] in ("SIM", "NÃO")
    assert "categoria" in result
    assert "resumo" in result
    assert "sugestao_resposta_ou_acao" in result


def test_analyze_handles_invalid_json():
    service = EmailAnalyzerService(client=FakeGeminiClient("not-json"))
    result = service.analyze("conteúdo qualquer")
    assert result.get("erro")
    assert "conteudo" in result



