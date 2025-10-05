from dataclasses import dataclass
import json
import logging
from typing import Dict, Any
from ..providers.gemini_client import GeminiClient


@dataclass
class EmailAnalyzerService:
    """
    Camada de serviço: prepara o prompt, chama o provedor (Gemini) e
    valida a saída (JSON). Mantém funções curtas e responsabilidades claras.
    """
    client: GeminiClient

    def build_prompt(self, email_content: str) -> str:
        return f"""Você é um assistente de IA que analisa e-mails e decide se eles precisam de atenção humana.

Leia o e-mail abaixo e responda **somente em JSON** no formato:

{{
  "atencao_humana": "SIM" ou "NÃO",
  "categoria": "string",
  "resumo": "string",
  "sugestao_resposta_ou_acao": "string"
}}

Regras resumidas:
- Se for proposta, parceria, dúvida, reclamação ou lead → "SIM".
- Se for elogio, felicitação, mensagem genérica ou spam → "NÃO".

E-mail para análise:
---
{email_content}
---"""

    def analyze(self, email_content: str) -> Dict[str, Any]:
        prompt = self.build_prompt(email_content)
        logging.debug("Enviando prompt ao Gemini (tamanho=%d)", len(prompt))
        result_str = self.client.generate_json(prompt)
        logging.debug("Resposta recebida (tamanho=%d)", len(result_str) if isinstance(result_str, str) else -1)
        try:
            result = json.loads(result_str)
        except (json.JSONDecodeError, TypeError):
            # Retorna mensagem estruturada em caso de falha de JSON
            logging.warning("Resposta não é JSON válido; retornando mensagem bruta")
            return {
                "erro": "A resposta do modelo não é um JSON válido",
                "conteudo": result_str,
            }
        return result


