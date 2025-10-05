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
**Você é um Analista de E-mails Corporativos.**

Analise a mensagem abaixo e forneça uma resposta estritamente no formato JSON, contendo:

1.  **"atencao_humana"**: (SIM/NÃO)
2.  **"categoria"**: (Escolha uma da lista abaixo)
3.  **"resumo"**: (Resumo conciso do conteúdo)
4.  **"sugestao_resposta_ou_acao"**: (Resposta automática ou próxima ação)

---

**REGRAS DE CLASSIFICAÇÃO:**

* **REQUER SIM (Ação Imediata)**: Negócios, Propostas, Parcerias, Reclamações, Dúvidas/Problemas Técnicos, Solicitações Importantes, Leads.
* **REQUER NÃO (Ação Automática)**: Spam, Marketing Genérico, Mensagens de Rotina, Felicitações/Elogios.

---

**CATEGORIAS POSSÍVEIS:**

Proposta Comercial, Parceria, Lead Qualificado, Reclamação, Dúvida Técnica, Solicitação de Informação, Spam, Mensagem Geral, Felicitação, Marketing Genérico.

---

E-mail para análise:
---
{email_content}
---
"""

    def analyze(self, email_content: str) -> Dict[str, Any]:
        prompt = self.build_prompt(email_content)
        logging.debug("Enviando prompt ao Gemini (tamanho=%d)", len(prompt))
        
        # A API do Gemini já garante a saída JSON quando solicitada, 
        # mas mantemos a validação defensiva.
        result_str = self.client.generate_json(prompt)
        
        logging.debug("Resposta recebida (tamanho=%d)", len(result_str) if isinstance(result_str, str) else -1)
        
        try:
            # Tenta carregar a string como JSON
            result = json.loads(result_str)
        except (json.JSONDecodeError, TypeError):
            # Retorna mensagem estruturada em caso de falha de JSON
            logging.warning("Resposta do modelo não é JSON válido.")
            return {
                "erro": "A resposta do modelo não é um JSON válido",
                "conteudo": result_str,
            }
        
        return result