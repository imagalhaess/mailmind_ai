from typing import Any
import google.generativeai as genai
from dataclasses import dataclass
import logging
import requests


@dataclass
class GeminiClient:
    """
    Encapsula configuração e criação do cliente Gemini.
    Responsabilidade única: fornecer acesso ao modelo configurado.
    """
    api_key: str
    model_name: str
    timeout: int = 600  # 10 minutos de timeout máximo

    def __post_init__(self) -> None:
        genai.configure(api_key=self.api_key)
        # Configura timeout global para requests
        import google.generativeai as genai
        if hasattr(genai, 'configure'):
            # Configura timeout para todas as requisições
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def generate_json(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1024) -> str:
        """
        Gera conteúdo em formato JSON (string) a partir do prompt fornecido.
        Levanta exceções para que a camada de serviço trate mensagens de erro.
        """
        import time
        import socket
        
        # Configura timeout para socket
        socket.setdefaulttimeout(self.timeout)
        
        model = genai.GenerativeModel(self.model_name)
        
        # Tenta com retry em caso de timeout
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logging.info(f"Tentativa {attempt + 1}/{max_retries} de chamada ao Gemini (timeout: {self.timeout}s)")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                    },
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Falha final após {max_retries} tentativas: {e}")
                    raise
                else:
                    logging.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente...")
                    time.sleep(2 ** attempt)  # Backoff exponencial
        
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
        import time
        import socket
        
        # Configura timeout para socket
        socket.setdefaulttimeout(self.timeout)
        
        model = genai.GenerativeModel(self.model_name)
        
        # Tenta com retry em caso de timeout
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logging.info(f"Tentativa {attempt + 1}/{max_retries} de chamada ao Gemini (timeout: {self.timeout}s)")
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                    },
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Falha final após {max_retries} tentativas: {e}")
                    raise
                else:
                    logging.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente...")
                    time.sleep(2 ** attempt)  # Backoff exponencial
        
        # Verifica se a resposta é válida antes de retornar
        if not response.candidates or not response.candidates[0].content.parts:
            raise ValueError("Resposta inválida do Gemini: nenhum conteúdo retornado")
        
        return response


