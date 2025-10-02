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
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    noreply_address: str = ""
    curator_address: str = ""


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

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    noreply_address = os.getenv("NOREPLY_ADDRESS", "")
    curator_address = os.getenv("CURATOR_ADDRESS", "")

    return AppConfig(
        gemini_api_key=gemini_api_key,
        model_name=model_name,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        noreply_address=noreply_address,
        curator_address=curator_address,
    )


