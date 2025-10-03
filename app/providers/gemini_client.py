from typing import Any
import google.generativeai as genai
from dataclasses import dataclass
import logging


@dataclass
class GeminiClient:
    """
    Encapsula configuração e criação do cliente Gemini.
    Responsabilidade única: fornecer acesso ao modelo configurado.
    """
    api_key: str
    model_name: str

    def __post_init__(self) -> None:
        genai.configure(api_key=self.api_key)

    def generate_json(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1024) -> str:
        """
        Gera conteúdo em formato JSON (string) a partir do prompt fornecido.
        Levanta exceções para que a camada de serviço trate mensagens de erro.
        """
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            },
        )
        
        # Verifica se a resposta é válida antes de acessar .text
        if not response.candidates or not response.candidates[0].content.parts:
            # Log detalhado para debug
            logging.error(f"Resposta inválida do Gemini: candidates={response.candidates}")
            if response.candidates:
                candidate = response.candidates[0]
                logging.error(f"Candidate: {candidate}")
                if hasattr(candidate, 'finish_reason'):
                    logging.error(f"Finish reason: {candidate.finish_reason}")
            raise ValueError("Resposta inválida do Gemini: nenhum conteúdo retornado")
        
        return response.text

    def generate_content(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1024):
        """
        Gera conteúdo em texto livre a partir do prompt fornecido.
        Retorna o objeto response completo para acesso a .text e .candidates.
        """
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            },
        )
        
        # Verifica se a resposta é válida antes de retornar
        if not response.candidates or not response.candidates[0].content.parts:
            raise ValueError("Resposta inválida do Gemini: nenhum conteúdo retornado")
        
        return response


