from typing import Any
import google.generativeai as genai
from dataclasses import dataclass


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
        return response.text


