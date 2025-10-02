import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    """
    AppConfig concentra variáveis de ambiente necessárias.
    Mantém uma única responsabilidade: carregar e validar configuração.
    """
    gemini_api_key: str
    model_name: str = "gemini-2.5-flash"


def load_config(dotenv_path: Optional[str] = None) -> AppConfig:
    """
    Carrega variáveis de ambiente do .env (se existir) e retorna AppConfig.
    Lança RuntimeError quando a chave não está definida.
    """
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path)
    else:
        load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY não encontrada. Defina no arquivo .env na raiz do projeto."
        )

    # Permite override do modelo via env, mas define um padrão seguro
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    return AppConfig(
        gemini_api_key=gemini_api_key,
        model_name=model_name,
    )


