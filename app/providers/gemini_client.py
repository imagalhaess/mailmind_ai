from typing import Any
import google.generativeai as genai
from dataclasses import dataclass
import logging
import requests
import time
import socket
import urllib3

# Configurações globais devem ser feitas fora das classes/funções
# Desabilita avisos de SSL se estiver usando proxies específicos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        # 1. Configura a API Key globalmente
        genai.configure(api_key=self.api_key)
        
        # 2. Configura o timeout padrão para requisições de socket (afeta a biblioteca `requests`)
        socket.setdefaulttimeout(self.timeout)
        
        # 3. Inicializa o modelo uma única vez
        self.model = genai.GenerativeModel(self.model_name)


    def _attempt_generate(self, prompt: str, is_json: bool, temperature: float, max_output_tokens: int) -> Any:
        """Helper interno para realizar a chamada e o retry com backoff."""
        max_retries = 3
        
        # Define a configuração de geração, incluindo JSON mime type se necessário
        config = {
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
        if is_json:
            config["response_mime_type"] = "application/json"
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Tentativa {attempt + 1}/{max_retries} de chamada ao Gemini (timeout: {self.timeout}s)")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=config,
                )
                
                # Sucesso: Retorna a resposta
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # Falha final
                    logging.error(f"Falha final após {max_retries} tentativas: {e}")
                    raise
                else:
                    # Tentativa falhou, espera e tenta novamente
                    logging.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente...")
                    time.sleep(2 ** attempt)  # Backoff exponencial


    def generate_json(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1024) -> str:
        """Gera conteúdo em formato JSON (string) a partir do prompt fornecido."""
        
        response = self._attempt_generate(
            prompt, 
            is_json=True, 
            temperature=temperature, 
            max_output_tokens=max_output_tokens
        )
        
        # Validação de Conteúdo: Acesso seguro ao texto da resposta
        if not response.candidates or not response.candidates[0].content.parts:
            logging.error(f"Resposta inválida do Gemini: candidates={response.candidates}")
            raise ValueError("Resposta inválida do Gemini: nenhum conteúdo retornado")
            
        return response.text


    def generate_content(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 1024):
        """Gera conteúdo em texto livre a partir do prompt fornecido. Retorna o objeto response completo."""
        
        response = self._attempt_generate(
            prompt, 
            is_json=False, 
            temperature=temperature, 
            max_output_tokens=max_output_tokens
        )
        
        # Validação de Conteúdo
        if not response.candidates or not response.candidates[0].content.parts:
            raise ValueError("Resposta inválida do Gemini: nenhum conteúdo retornado")
            
        return response