from dataclasses import dataclass
import json
import logging
from typing import Dict, Any
try:
    from ..providers.gemini_client import GeminiClient
except ImportError:
    from providers.gemini_client import GeminiClient


@dataclass
class EmailAnalyzerService:
    """
    Camada de serviço: prepara o prompt, chama o provedor (Gemini) e
    valida a saída (JSON). Mantém funções curtas e responsabilidades claras.
    """
    client: GeminiClient

    def build_prompt(self, email_content: str) -> str:
        return f"""Analise este email corporativo e responda APENAS em JSON válido.

INSTRUÇÕES:
- Categorize corretamente
- Sugira ação específica
- Determine se precisa de curadoria humana
- NO RESUMO: Faça um resumo completo do conteúdo do email, incluindo quem enviou, o assunto e os pontos principais

CATEGORIAS: Spam, Produtivo, Reclamação, Consulta, Urgente, Outro

Responda APENAS em JSON:

{{
  "atencao_humana": "SIM" ou "NÃO",
  "categoria": "uma das categorias acima",
  "resumo": "resumo completo do conteúdo do email: remetente, assunto e pontos principais",
  "sugestao_resposta_ou_acao": "sugestão específica de ação",
  "acao": "RESPOSTA_AUTOMATICA" ou "ENCAMINHAR_CURADORIA"
}}

Email: {email_content}"""

    def analyze(self, email_content: str) -> Dict[str, Any]:
        prompt = self.build_prompt(email_content)
        logging.debug("Enviando prompt ao Gemini (tamanho=%d)", len(prompt))
        
        try:
            result_str = self.client.generate_json(prompt)
            logging.debug("Resposta recebida (tamanho=%d)", len(result_str) if isinstance(result_str, str) else -1)
            
            # Tenta fazer parse do JSON
            result = json.loads(result_str)
            
            # Valida se tem os campos mínimos necessários
            if "categoria" not in result:
                logging.warning("Resposta JSON sem campo 'categoria', tentando extrair")
                # Retorna estrutura padrão se não tiver categoria
                return {
                    "categoria": "Outro",
                    "atencao_humana": "SIM",
                    "resumo": result.get("resumo", "Análise incompleta"),
                    "sugestao_resposta_ou_acao": result.get("sugestao_resposta_ou_acao", "Revisar manualmente"),
                    "acao": "ENCAMINHAR_CURADORIA"
                }
            
            return result
            
        except (json.JSONDecodeError, TypeError) as e:
            # Retorna estrutura padrão em caso de falha de JSON
            logging.error(f"Erro ao fazer parse do JSON: {e}")
            logging.warning(f"Resposta do Gemini: {result_str[:200]}...")
            
            return {
                "categoria": "Outro",
                "atencao_humana": "SIM",
                "resumo": "Erro ao processar resposta do modelo de IA",
                "sugestao_resposta_ou_acao": "Revisar manualmente - resposta do modelo não estava no formato esperado",
                "acao": "ENCAMINHAR_CURADORIA"
            }
        except Exception as e:
            logging.error(f"Erro inesperado na análise: {e}")
            return {
                "categoria": "Erro",
                "atencao_humana": "SIM",
                "resumo": f"Erro ao analisar email: {str(e)}",
                "sugestao_resposta_ou_acao": "Revisar manualmente",
                "acao": "ENCAMINHAR_CURADORIA"
            }


