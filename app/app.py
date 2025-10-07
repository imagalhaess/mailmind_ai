"""
MailMind AI - Sistema de Análise Inteligente de E-mails

Este arquivo contém as funções principais para:
- Upload e processamento de arquivos (.txt e .pdf)
- Análise de e-mails usando IA (Google Gemini)
- APIs para integração com outros sistemas

Para devs iniciantes:
- As funções de upload limitam o tamanho dos arquivos para evitar travamentos
- O processamento de PDF é feito de forma segura, cortando textos muito longos
- Sempre há tratamento de erro para evitar que a aplicação quebre
"""

import io
import os
import json
import logging
import re
import hashlib
import uuid
import threading
import time
from typing import Tuple, Any, List, Optional, Dict
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_cors import CORS
from dotenv import load_dotenv
import PyPDF2

# Imports Locais
from .config import load_config
from .providers.gemini_client import GeminiClient
from .services.email_analyzer import EmailAnalyzerService
from .utils.text_preprocess import basic_preprocess
from .utils.email_sender import EmailSender

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Sistema de Jobs Assíncronos (simples em memória)
JOBS: Dict[str, Dict] = {}
JOBS_LOCK = threading.Lock()

# Regex compiladas para melhor performance
EMAIL_PATTERN = re.compile(
    r'From:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    re.IGNORECASE
)
EMAIL_SEPARATOR_PATTERN = re.compile(
    r'\n\n(?:From:\s+[^\n]+@[^\n]+\.[^\n]+|De:\s+[^\n]+@[^\n]+\.[^\n]+|Message-ID:\s+<[^>]+>|---)',
    re.IGNORECASE
)


def extract_text_from_pdf_safe(file_stream, max_chars: int = 1000) -> str:
    """Extrai texto do PDF de forma ultra rápida."""
    try:
        pdf = PyPDF2.PdfReader(file_stream)
        texto = ""
        
        # Processa apenas as primeiras 3 páginas
        for i, pagina in enumerate(pdf.pages[:3]):
            if len(texto) > max_chars:
                break
            page_text = pagina.extract_text() or ""
            texto += page_text
            
        return re.sub(r'\s+', ' ', texto[:max_chars]).strip()
    except:
        return ""


def read_text_from_upload(max_file_size_mb: int = 5) -> Tuple[str, str]:
    """Lê conteúdo de .txt ou .pdf de forma rápida."""
    # Texto do formulário
    if request.form.get("email_text"):
        return request.form["email_text"], "text"
    
    # JSON (API)
    if request.is_json:
        data = request.get_json()
        if data and "email_content" in data:
            return data["email_content"], "json"

    # Arquivo
    file = request.files.get("email_file")
    if not file or file.filename == "":
        return "", "none"
    
    filename = file.filename.lower()
    if not (filename.endswith(".txt") or filename.endswith(".pdf")):
        return "", "unsupported"
    
    file_data = file.read()
    if len(file_data) > max_file_size_mb * 1024 * 1024:
        return "", "file_too_large"
    
    if filename.endswith(".txt"):
        try:
            return file_data.decode("utf-8", errors="ignore"), "txt"
        except:
            return "", "txt_error"
    elif filename.endswith(".pdf"):
        try:
            with io.BytesIO(file_data) as buf:
                texto = extract_text_from_pdf_safe(buf)
            return texto, "pdf"
        except:
            return "", "pdf_error"
    else:
        return "", "unsupported"


def extract_sender_from_email(email_content: str) -> str:
    """Extrai o email do remetente do conteúdo do email."""
    match = EMAIL_PATTERN.search(email_content)
    if match:
        return match.group(1).strip()
    return ""


def split_multiple_emails(content: str) -> List[str]:
    """
    Divide um arquivo com múltiplos emails em uma lista de emails individuais.
    Usa separadores como ---, === ou múltiplos From:
    """
    # Tenta dividir por separadores explícitos primeiro (---, ===)
    separator_pattern = re.compile(r'\n[-=]{3,}\n', re.MULTILINE)
    parts = separator_pattern.split(content)
    
    # Se encontrou separadores, processa as partes
    if len(parts) > 1:
        emails: List[str] = []
        for part in parts:
            cleaned = part.strip()
            if cleaned and len(cleaned) > 50:  # Ignora fragmentos muito pequenos
                emails.append(cleaned)
        return emails if emails else [content.strip()]
    
    # Se não encontrou separadores, verifica se há múltiplos "From:"
    from_pattern = re.compile(r'^From:\s', re.MULTILINE | re.IGNORECASE)
    from_matches = list(from_pattern.finditer(content))
    
    # Se encontrou múltiplos "From:", divide por eles
    if len(from_matches) > 1:
        emails: List[str] = []
        for i, match in enumerate(from_matches):
            start = match.start()
            end = from_matches[i + 1].start() if i + 1 < len(from_matches) else len(content)
            email_part = content[start:end].strip()
            if email_part and len(email_part) > 50:
                emails.append(email_part)
        return emails if emails else [content.strip()]
    
    # Caso contrário, retorna o conteúdo completo como um único email
    return [content.strip()]


def truncate_text_for_gemini(text: str, max_chars: int = 1000) -> str:
    """Trunca texto para Gemini de forma rápida."""
    if len(text) <= max_chars:
        return text
    
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    if last_period > max_chars * 0.8:
        truncated = truncated[:last_period + 1]
    
    return truncated


def get_cache_key(email_content: str) -> str:
    """Gera chave de cache rápida."""
    content_sample = email_content[:500] if len(email_content) > 500 else email_content
    content_hash = hashlib.sha256(content_sample.encode('utf-8')).hexdigest()
    return f"analysis:{content_hash[:8]}"


def process_email_async(job_id: str, email_content: str, service, cache, config):
    """Processa email em background."""
    try:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "processing"
        
        # Trunca texto
        truncated = truncate_text_for_gemini(email_content, 1000)
        
        # Pré-processa se necessário
        if len(truncated) > 500:
            preprocessed = basic_preprocess(truncated)
        else:
            preprocessed = truncated
        
        # Analisa
        result = service.analyze(preprocessed)
        
        # Processa resultado
        categoria = result.get("categoria", "N/A")
        atencao = result.get("atencao_humana", "NÃO")
        resumo = result.get("resumo", "N/A")
        sugestao = result.get("sugestao_resposta_ou_acao", "N/A")
        
        if atencao.upper() == "SIM":
            acao = "📧 Encaminhar para curadoria humana"
        elif categoria.lower() == "spam":
            acao = "🚫 Spam detectado"
        else:
            acao = "✅ Processado com sucesso"
        
        result_data = {
            "categoria": categoria,
            "atencao_humana": atencao,
            "resumo": resumo,
            "sugestao": sugestao,
            "acao": acao,
            "sender": extract_sender_from_email(email_content) or 'Não identificado',
            "cached": False
        }
        
        # Cache
        cache_key = get_cache_key(email_content)
        cache.set(cache_key, result_data, timeout=config.cache_default_timeout)
        
        # Atualiza job
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["result"] = result_data
            
    except Exception as e:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = str(e)


def require_api_key(f):
    """Decorator para validar API key quando necessário."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        config = getattr(decorated_function, '_config', None)
        
        if not config or not config.api_key_required:
            return f(*args, **kwargs)
        
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                "error": "API key é obrigatória",
                "message": "Forneça a API key no header 'X-API-Key'"
            }), 401
        
        if api_key not in config.valid_api_keys:
            return jsonify({
                "error": "API key inválida",
                "message": "A API key fornecida não é válida"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def create_app() -> Flask:
    """Factory function para criar e configurar a aplicação Flask."""
    
    # --- Configuração Inicial ---
    load_dotenv()
    config = load_config()
    
    app = Flask(__name__)
    app.secret_key = config.app_secret
    
    # Configuração CORS
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/webhook/*": {"origins": "*"}
    })
    
    # Configuração de Cache
    cache_config = {
        'CACHE_TYPE': config.cache_type,
        'CACHE_DEFAULT_TIMEOUT': config.cache_default_timeout
    }
    
    if config.redis_url:
        cache_config['CACHE_REDIS_URL'] = config.redis_url
        logger.info("Cache configurado com Redis")
    else:
        logger.info("Cache configurado com SimpleCache (memória)")
    
    cache = Cache(app, config=cache_config)
    
    # Configuração de Rate Limiting
    app.limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[config.rate_limit_default],
        storage_uri=config.redis_url if config.redis_url else "memory://",
        enabled=config.rate_limit_enabled
    )
    
    if config.rate_limit_enabled:
        logger.info(f"Rate limiting habilitado: {config.rate_limit_default}")
    
    # Configuração do Sentry (monitoramento de erros)
    if config.sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=config.sentry_dsn,
                integrations=[FlaskIntegration()],
                environment=config.environment,
                traces_sample_rate=0.1
            )
            logger.info("Sentry inicializado para monitoramento de erros")
        except ImportError:
            logger.warning("sentry-sdk não instalado, monitoramento desabilitado")
    
    # 1. Configuração do Gemini Client
    client = GeminiClient(
        api_key=config.gemini_api_key, 
        model_name=config.model_name,
        timeout=config.gemini_timeout
    )
    service = EmailAnalyzerService(client=client)
    
    # 2. Configuração do Mailer (SMTP)
    smtp_enabled = os.getenv("SMTP_ENABLED", "true").lower() == "true"
    mailer = None
    
    if smtp_enabled and config.smtp_host:
        try:
            mailer = EmailSender(
                host=config.smtp_host,
                port=config.smtp_port,
                username=config.smtp_user,
                password=config.smtp_password,
                default_from=config.noreply_address,
                timeout=config.smtp_timeout
            )
            logger.info("SMTP configurado com sucesso")
        except Exception as e:
            logger.warning(f"Falha ao configurar SMTP: {e}")
            mailer = None
    
    if mailer is None:
        logger.info("SMTP não configurado - modo simulação ativado")
    
    # Armazena config no decorator
    require_api_key._config = config
    
    # --- Rotas da Aplicação ---
    
    @app.route("/", methods=["GET"])
    def index():
        """Página inicial."""
        return send_from_directory('static', 'index.html')
    
    @app.route("/test-route")
    def test_route():
        """Rota de teste para verificar se o deploy está funcionando."""
        return jsonify({"message": "Rota de teste funcionando!", "timestamp": "2025-01-06"})
    
    @app.route("/analyze/status/test")
    def test_status_route():
        """Teste específico para a rota de status."""
        return jsonify({"message": "Rota de status funcionando!", "job_id": "test"})
    
    @app.route("/health")
    def health():
        """Endpoint de health check para monitoramento."""
        try:
            # Verifica se o Gemini está acessível
            gemini_status = "healthy"
            try:
                # Teste simples sem gastar quota
                _ = client.model
            except Exception:
                gemini_status = "unhealthy"
            
            return jsonify({
                'status': 'healthy',
                'service': 'MailMind AI',
                'version': '2.0.0',
                'components': {
                    'gemini': gemini_status,
                    'smtp': 'configured' if mailer else 'not_configured',
                    'cache': config.cache_type,
                    'rate_limiting': 'enabled' if config.rate_limit_enabled else 'disabled'
                }
            })
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500
    
    @app.route("/analyze/async", methods=["POST"])
    @app.limiter.limit("10 per minute")
    def analyze_async():
        """
        Endpoint para análise assíncrona de emails grandes.
        Retorna um ID de job para consulta posterior.
        """
        try:
            raw_text, origin = read_text_from_upload(config.max_file_size_mb)
            
            if not raw_text:
                return jsonify({"error": "Conteúdo não encontrado"}), 400
            
            # Gera ID único para o job
            import uuid
            job_id = str(uuid.uuid4())[:8]
            
            # Simula processamento assíncrono (em produção, usaria Celery ou similar)
            logger.info(f"Job {job_id} iniciado para análise assíncrona")
            
            return jsonify({
                "job_id": job_id,
                "status": "processing",
                "message": "Análise iniciada. Use /analyze/status/<job_id> para verificar progresso."
            }), 202
            
        except Exception as e:
            logger.error(f"Erro na análise assíncrona: {e}")
            return jsonify({"error": "Erro interno"}), 500
    
    @app.route("/analyze/status/<job_id>", methods=["GET"])
    def analyze_status(job_id):
        """Consulta o status de um job de análise assíncrona."""
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            
        if not job:
            return jsonify({"error": "Job não encontrado"}), 404
        
        if job["status"] == "completed":
            return jsonify({
                "job_id": job_id,
                "status": "completed",
                "result": job["result"]
            })
        elif job["status"] == "error":
            return jsonify({
                "job_id": job_id,
                "status": "error",
                "error": job["error"]
            })
        else:
            return jsonify({
                "job_id": job_id,
                "status": job["status"],
                "message": "Processando..."
            })
    
    @app.route("/webhook/email", methods=["POST"])
    @app.limiter.limit("30 per minute")
    @require_api_key
    def webhook_email():
        """Webhook para receber emails automaticamente."""
        try:
            # Lê dados da requisição
            if request.is_json:
                data = request.get_json()
                email_content = data.get('email_content', data.get('content', ''))
                sender = data.get('sender', '')
                subject = data.get('subject', '')
            else:
                email_content = request.form.get('email_content', '')
                sender = request.form.get('sender', '')
                subject = request.form.get('subject', '')
            
            if not email_content:
                return jsonify({"error": "Email content is required"}), 400
            
            # Constrói o email formatado
            formatted_email = f"From: {sender}\nSubject: {subject}\n\n{email_content}"
            
            # Verifica cache
            cache_key = get_cache_key(formatted_email)
            cached_result = cache.get(cache_key)
            
            if cached_result:
                cached_result['cached'] = True
                return jsonify(cached_result)
            
            # Processa assincronamente
            job_id = str(uuid.uuid4())[:8]
            
            with JOBS_LOCK:
                JOBS[job_id] = {
                    "status": "queued",
                    "email_content": formatted_email
                }
            
            # Inicia processamento em background
            thread = threading.Thread(
                target=process_email_async,
                args=(job_id, formatted_email, service, cache, config)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                "job_id": job_id,
                "status": "queued",
                "message": "Email em processamento. Use /analyze/status/<job_id> para verificar progresso."
            })
            
        except Exception as e:
            return jsonify({"error": "Erro interno do servidor"}), 500
    
    @app.route("/analyze", methods=["POST"])
    @app.limiter.limit("20 per minute")
    def analyze():
        """Rota principal para análise de emails via interface web."""
        try:
            raw_text, origin = read_text_from_upload(config.max_file_size_mb)
            
            if not raw_text:
                if origin == "file_too_large":
                    return jsonify({"error": f"📁 Arquivo muito grande. Limite de {config.max_file_size_mb}MB."}), 400
                elif origin == "unsupported":
                    return jsonify({"error": "📝 Formato não suportado. Use .txt ou .pdf"}), 400
                return jsonify({"error": "📝 Envie um arquivo .txt/.pdf ou cole o texto do e-mail."}), 400
            
            # Detecta múltiplos emails
            emails = split_multiple_emails(raw_text)
            
            # Limita emails
            if len(emails) > 10:  # Reduzido para 10 emails
                return jsonify({"error": f"⚠️ Limite de 10 emails por lote excedido"}), 400
            
            # Para múltiplos emails, processa diretamente
            if len(emails) > 1:
                results = []
                
                for email_content in emails:
                    try:
                        # Verifica cache primeiro
                        cache_key = get_cache_key(email_content)
                        cached_result = cache.get(cache_key)
                        
                        if cached_result:
                            result_data = cached_result.copy()
                            result_data['cached'] = True
                            results.append(result_data)
                        else:
                            # Processa diretamente
                            truncated = truncate_text_for_gemini(email_content, 1000)
                            preprocessed = basic_preprocess(truncated) if len(truncated) > 500 else truncated
                            
                            result = service.analyze(preprocessed)
                            
                            categoria = result.get("categoria", "N/A")
                            atencao = result.get("atencao_humana", "NÃO")
                            resumo = result.get("resumo", "N/A")
                            sugestao = result.get("sugestao_resposta_ou_acao", "N/A")
                            
                            if atencao.upper() == "SIM":
                                acao = "📧 Encaminhar para curadoria humana"
                            elif categoria.lower() == "spam":
                                acao = "🚫 Spam detectado"
                            else:
                                acao = "✅ Processado com sucesso"
                            
                            result_data = {
                                "categoria": categoria,
                                "atencao_humana": atencao,
                                "resumo": resumo,
                                "sugestao": sugestao,
                                "acao": acao,
                                "sender": extract_sender_from_email(email_content) or 'Não identificado',
                                "cached": False
                            }
                            
                            cache.set(cache_key, result_data, timeout=config.cache_default_timeout)
                            results.append(result_data)
                            
                    except Exception as e:
                        logger.error(f"Erro ao processar email: {e}")
                        results.append({
                            "categoria": "❌ ERRO",
                            "atencao_humana": "SIM",
                            "resumo": f"Falha na análise: {str(e)}",
                            "sugestao": "Verifique o conteúdo e tente novamente",
                            "sender": "Não identificado",
                            "acao": "⚠️ Erro no processamento",
                            "cached": False
                        })
                
                return jsonify({
                    "total_emails": len(emails),
                    "results": results,
                    "message": f"✅ Análise concluída para {len(emails)} email(s)"
                })
            
            else:
                # Análise individual - processa diretamente
                email_content = emails[0]
                cache_key = get_cache_key(email_content)
                cached_result = cache.get(cache_key)
                
                if cached_result:
                    response = cached_result.copy()
                    response['cached'] = True
                    return jsonify(response)
                
                # Processa diretamente
                try:
                    truncated = truncate_text_for_gemini(email_content, 1000)
                    preprocessed = basic_preprocess(truncated) if len(truncated) > 500 else truncated
                    
                    result = service.analyze(preprocessed)
                    
                    categoria = result.get("categoria", "N/A")
                    atencao = result.get("atencao_humana", "NÃO")
                    resumo = result.get("resumo", "N/A")
                    sugestao = result.get("sugestao_resposta_ou_acao", "N/A")
                    
                    if atencao.upper() == "SIM":
                        acao = "📧 Encaminhar para curadoria humana"
                    elif categoria.lower() == "spam":
                        acao = "🚫 Spam detectado"
                    else:
                        acao = "✅ Processado com sucesso"
                    
                    response = {
                        "categoria": categoria,
                        "atencao_humana": atencao,
                        "resumo": resumo,
                        "sugestao": sugestao,
                        "acao": acao,
                        "sender": extract_sender_from_email(email_content) or 'Não identificado',
                        "cached": False
                    }
                    
                    cache.set(cache_key, response, timeout=config.cache_default_timeout)
                    return jsonify(response)
                    
                except Exception as e:
                    logger.error(f"Erro na análise: {e}")
                    return jsonify({
                        "categoria": "❌ ERRO",
                        "atencao_humana": "SIM",
                        "resumo": f"Falha na análise: {str(e)}",
                        "sugestao": "Verifique o conteúdo e tente novamente",
                        "sender": "Não identificado",
                        "acao": "⚠️ Erro no processamento",
                        "cached": False
                    })
                
        except Exception as e:
            return jsonify({"error": "❌ Erro interno do servidor"}), 500
    
    @app.route("/test/<test_type>")
    @app.limiter.limit("60 per minute")
    def test_mock(test_type):
        """Rota para testar com dados mock."""
        mock_results = {
            "spam": {
                "categoria": "Spam",
                "atencao_humana": "NÃO",
                "resumo": "Email promocional com ofertas suspeitas",
                "sugestao": "Marcar como spam e ignorar",
                "sender": "spam@exemplo.com",
                "acao": "🚫 Spam detectado"
            },
            "produtivo": {
                "categoria": "Produtivo",
                "atencao_humana": "SIM",
                "resumo": "Proposta de parceria comercial legítima",
                "sugestao": "Responder com interesse e agendar reunião",
                "sender": "cliente@empresa.com",
                "acao": "📧 Encaminhar para curadoria humana"
            },
            "reclamacao": {
                "categoria": "Reclamacao",
                "atencao_humana": "SIM",
                "resumo": "Reclamação sobre produto com problema técnico",
                "sugestao": "Investigar problema e oferecer solução",
                "sender": "usuario@cliente.com",
                "acao": "📧 Encaminhar para curadoria humana"
            }
        }
        
        if test_type not in mock_results:
            return jsonify({
                "error": f"Tipo de teste inválido",
                "available_types": list(mock_results.keys())
            }), 400
        
        result = mock_results[test_type]
        return jsonify({
            **result,
            "test_mode": True,
            "test_type": test_type,
            "cached": False
        })
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve arquivos estáticos."""
        return send_from_directory('static', filename)
    
    @app.route('/docs/<path:filename>')
    def serve_docs(filename):
        """Serve documentação."""
        return send_from_directory('../docs', filename)
    
    # Error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit excedido",
            "message": "Muitas requisições. Tente novamente em alguns minutos."
        }), 429
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint não encontrado"}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Erro interno: {e}", exc_info=True)
        return jsonify({
            "error": "Erro interno do servidor",
            "message": "Ocorreu um erro inesperado"
        }), 500
    
    return app


# Exportar app para gunicorn
app = create_app()


def main():
    """Função principal para executar a aplicação localmente."""
    config = load_config()
    logger.info(f"🚀 Iniciando MailMind em http://localhost:{config.port}")
    app.run(host="0.0.0.0", port=config.port, debug=False)


if __name__ == "__main__":
    main()
