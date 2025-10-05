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
        return f"""Analise este email e responda em JSON:

{{
  "atencao_humana": "SIM" ou "NÃO",
  "categoria": "Spam/Produtivo/Reclamacao/Outro",
  "resumo": "resumo curto",
  "sugestao_resposta_ou_acao": "acao sugerida"
}}

Email: {email_content}"""

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


