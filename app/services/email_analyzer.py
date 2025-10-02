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
        return f"""
        Você é um assistente de IA especializado em análise de e-mails para uma empresa financeira.
        Sua tarefa é analisar o seguinte e-mail e fornecer:
        1. Uma classificação da necessidade de atenção humana (SIM/NÃO).
        2. Uma categoria para o e-mail (e.g., 'Solicitação de Status', 'Informação Geral', 'Reclamação', 'Elogio', 'Spam', 'Outro').
        3. Um resumo conciso do e-mail.
        4. Uma sugestão de resposta automática, se o e-mail não exigir atenção humana. Se exigir atenção humana, sugira uma ação para a equipe humana.

        Formato da saída esperada (JSON):
        {{
            "atencao_humana": "SIM" | "NÃO",
            "categoria": "string",
            "resumo": "string",
            "sugestao_resposta_ou_acao": "string"
        }}

        E-mail para análise:
        ---
        {email_content}
        ---
        """

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


