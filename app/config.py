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
    app_secret: str = "dev-secret"
    port: int = 8001
    
    # Configurações de performance
    max_file_size_mb: int = 10  # Aumentado para 10MB
    max_pdf_chars: int = 50000  # Aumentado para 50k caracteres
    max_batch_size: int = 50
    smtp_timeout: int = 60  # Aumentado para 60 segundos
    gemini_timeout: int = 600  # 10 minutos para Gemini
    request_timeout: int = 600  # 10 minutos para requisições HTTP
    
    # Configurações de cache
    cache_type: str = "SimpleCache"
    cache_default_timeout: int = 3600
    redis_url: Optional[str] = None
    
    # Configurações de segurança
    rate_limit_enabled: bool = True
    rate_limit_default: str = "100 per hour"
    api_key_required: bool = False
    valid_api_keys: list = None
    
    # Configurações de monitoramento
    sentry_dsn: Optional[str] = None
    environment: str = "development"


def load_config(dotenv_path: Optional[str] = None) -> AppConfig:
    """
    Carrega variáveis de ambiente do .env (se existir) e retorna AppConfig.
    Lança RuntimeError quando a chave obrigatória não está definida.
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

    # SMTP Configuration
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    noreply_address = os.getenv("NOREPLY_ADDRESS", "")
    curator_address = os.getenv("CURATOR_ADDRESS", "")
    
    # App Configuration
    app_secret = os.getenv("APP_SECRET", "dev-secret")
    port = int(os.getenv("PORT", "8001"))
    
    # Performance Configuration
    max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    max_pdf_chars = int(os.getenv("MAX_PDF_CHARS", "50000"))
    max_batch_size = int(os.getenv("MAX_BATCH_SIZE", "50"))
    smtp_timeout = int(os.getenv("SMTP_TIMEOUT", "60"))
    gemini_timeout = int(os.getenv("GEMINI_TIMEOUT", "600"))
    request_timeout = int(os.getenv("REQUEST_TIMEOUT", "600"))
    
    # Cache Configuration
    cache_type = os.getenv("CACHE_TYPE", "SimpleCache")
    cache_default_timeout = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "3600"))
    redis_url = os.getenv("REDIS_URL")
    
    # Security Configuration
    rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_default = os.getenv("RATE_LIMIT_DEFAULT", "100 per hour")
    api_key_required = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
    
    # Parse API keys from comma-separated string
    api_keys_str = os.getenv("VALID_API_KEYS", "")
    valid_api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()] if api_keys_str else []
    
    # Monitoring Configuration
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")

    return AppConfig(
        gemini_api_key=gemini_api_key,
        model_name=model_name,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        noreply_address=noreply_address,
        curator_address=curator_address,
        app_secret=app_secret,
        port=port,
        max_file_size_mb=max_file_size_mb,
        max_pdf_chars=max_pdf_chars,
        max_batch_size=max_batch_size,
        smtp_timeout=smtp_timeout,
        gemini_timeout=gemini_timeout,
        request_timeout=request_timeout,
        cache_type=cache_type,
        cache_default_timeout=cache_default_timeout,
        redis_url=redis_url,
        rate_limit_enabled=rate_limit_enabled,
        rate_limit_default=rate_limit_default,
        api_key_required=api_key_required,
        valid_api_keys=valid_api_keys,
        sentry_dsn=sentry_dsn,
        environment=environment,
    )
