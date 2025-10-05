from typing import Any
import google.generativeai as genai
from dataclasses import dataclass
import logging
import time


@dataclass
class GeminiClient:
    """
    Encapsula configuração e criação do cliente Gemini.
    Responsabilidade única: fornecer acesso ao modelo configurado.
    """
    api_key: str
    model_name: str
    timeout: int = 120  # 2 minutos de timeout (reduzido de 10 minutos)

    def __post_init__(self) -> None:
        # 1. Configura a API Key globalmente
        genai.configure(api_key=self.api_key)
        
        # 2. Inicializa o modelo uma única vez
        self.model = genai.GenerativeModel(self.model_name)
        
        logging.info(f"GeminiClient inicializado com modelo: {self.model_name}")

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
                logging.info(f"Tentativa {attempt + 1}/{max_retries} de chamada ao Gemini")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=config,
                    request_options={"timeout": self.timeout}
                )
                
                # Sucesso: Retorna a resposta
                logging.info("Chamada ao Gemini bem-sucedida")
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # Falha final
                    logging.error(f"Falha final após {max_retries} tentativas: {e}")
                    raise
                else:
                    # Tentativa falhou, espera e tenta novamente
                    wait_time = 2 ** attempt
                    logging.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {wait_time}s...")
                    time.sleep(wait_time)  # Backoff exponencial

    def generate_json(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 2048) -> str:
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

    def generate_content(self, prompt: str, *, temperature: float = 0.2, max_output_tokens: int = 2048):
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
