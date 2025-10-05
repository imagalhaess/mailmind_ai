import io
import os
import json
import logging
import re # Movido para o topo, pois era usado dentro de funções
import threading
from typing import Tuple, Any, List, Optional
from flask import Flask, request, jsonify, send_from_directory, flash, redirect, url_for
from dotenv import load_dotenv
import PyPDF2

# Imports Locais
from .config import load_config
from .providers.gemini_client import GeminiClient
from .services.email_analyzer import EmailAnalyzerService
from .utils.text_preprocess import basic_preprocess
from .utils.email_sender import EmailSender


def extract_text_from_pdf_safe(file_stream) -> str:
    """
    Extrai texto de PDF de forma segura, limitando o tamanho para evitar timeouts
    e falhas de memória.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        max_chars = 20000  # Limite preventivo
        
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            text += page_text
            
            # Para se atingir o limite de caracteres
            if len(text) > max_chars:
                text = text[:max_chars]
                break
                
        # Garante que não haja quebras de linha duplas desnecessárias
        return re.sub(r'\n\s*\n', '\n', text).strip()
    except Exception as e:
        # Simplifica o log de erro para ser menos verboso
        logging.error(f"Erro ao processar PDF: {e}")
        return ""


def read_text_from_upload() -> Tuple[str, str]:
    """
    Lê o conteúdo do upload suportando .txt/.pdf, campo de texto e JSON.
    Retorna (conteudo, origem) para logging.
    """
    # Suporte a JSON (API)
    if request.is_json:
        data = request.get_json()
        if data and "email_content" in data:
            return data["email_content"], "json"
    
    # Suporte a formulário (interface web)
    if request.form.get("email_text"):
        return request.form["email_text"], "text"

    file = request.files.get("email_file")
    if not file or file.filename == "":
        return "", "none"
    
    # Limite de tamanho de arquivo (2MB)
    MAX_FILE_SIZE_MB = 2
    if file.content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
        return "", "file_too_large"

    filename = file.filename.lower()
    data = file.read()

    if filename.endswith(".txt"):
        # Use o .decode nativo
        return data.decode("utf-8", errors="ignore"), "txt"
    if filename.endswith(".pdf"):
        with io.BytesIO(data) as buf:
            # Usa processamento seguro de PDF e retorna o texto limpo
            text = extract_text_from_pdf_safe(buf)
            # A lógica de limpeza e fallback para PDF foi movida para dentro de extract_text_from_pdf_safe
            return text, "pdf"

    return "", "unsupported"


def extract_sender_from_email(email_content: str) -> str:
    """Extrai o email do remetente do conteúdo do email."""
    # Padrões comuns para identificar remetente
    patterns = [
        r'From:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'De:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'Remetente:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'Sender:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'Enviado por:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, email_content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""


def generate_automatic_response(sugestao, categoria, email_content, sender_email=""):
    """
    Gera uma resposta automática personalizada usando IA
    NOTA: Mantendo a estrutura original para evitar mudar a lógica de prompt
    """
    try:
        # Importação local movida para evitar circular dependency issues
        from .services.email_analyzer import EmailAnalyzerService
        from .providers.gemini_client import GeminiClient
        from .config import load_config
        
        config = load_config()
        # Reutiliza o cliente e modelo configurado no create_app, se possível,
        # mas aqui cria um novo para manter a independência da função.
        client = GeminiClient(api_key=config.gemini_api_key, model_name=config.model_name)
        
        # Lógica de extração de nome removida para simplificar o prompt
        
        # Prompt melhorado para gerar resposta automática
        prompt = f"""
        Você é um assistente de IA especializado em gerar respostas automáticas educadas e personalizadas para emails corporativos.

        CONTEXTO:
        - Empresa: MailMind (sistema de análise de emails)
        - Categoria do email recebido: "{categoria}"
        - Sugestão de ação: "{sugestao}"
        - Conteúdo original do email: "{email_content[:500]}..."

        INSTRUÇÕES ESPECÍFICAS:
        Gere uma resposta automática completa e personalizada que:

        1. **ABERTURA CORDIAL**: Comece com "Olá," seguido de agradecimento específico
        2. **EXPLICAÇÃO CLARA**: Explique que a mensagem foi analisada automaticamente pelo sistema MailMind
        3. **RESPOSTA CONTEXTUAL**: Baseie sua resposta na categoria específica
        4. **ORIENTAÇÃO CLARA**: Indique que não requer atenção imediata da equipe (a menos que a sugestão/categoria indique o contrário)
        5. **CANAL ALTERNATIVO**: Sugira contato através dos canais oficiais se necessário
        6. **INSTRUÇÃO IMPORTANTE**: Inclua "Esta é uma resposta automática gerada pelo nosso sistema de análise de emails, por favor, não responda para este endereço."
        7. **ASSINATURA**: Termine com "Atenciosamente, Equipe MailMind"

        FORMATO DA RESPOSTA:
        - Use parágrafos bem estruturados
        - Mantenha tom profissional mas caloroso
        - A resposta deve estar pronta para envio direto (NÃO use aspas no início/fim)

        Gere uma resposta completa e personalizada agora:
        """
        
        # Gerando resposta automática (usando generate_content para texto livre)
        response = client.generate_content(prompt)
        
        # Usa response.text que é garantido após a validação no cliente
        return response.text.strip()
            
    except Exception as e:
        logging.error(f"Erro ao gerar resposta automática: {e}")
        # Fallback para resposta padrão em caso de erro
        return "Obrigado pelo contato. Sua mensagem foi recebida e será analisada pela nossa equipe."


def split_multiple_emails(content: str) -> list:
    """
    Divide um arquivo com múltiplos emails em uma lista de emails individuais.
    Lógica de divisão simplificada e centralizada no re.split.
    """
    # Padrões mais robustos para identificar início de novos emails
    email_separators = [
        r'\n\nFrom:\s+[^\n]+@[^\n]+\.[^\n]+',    # From: email@domain.com
        r'\n\nDe:\s+[^\n]+@[^\n]+\.[^\n]+',     # De: email@domain.com
        r'\n\nMessage-ID:\s+<[^>]+>',          # Message-ID: <id>
        r'\n\n---\n',                           # Separador explícito
    ]
    
    # Cria uma regex combinada para dividir
    combined_regex = f"({'|'.join(email_separators)})"
    
    # Divide, mantendo os separadores na lista para tentar reconstruir
    parts = re.split(combined_regex, content, flags=re.IGNORECASE)
    
    emails: List[str] = []
    
    # Reconstroi as mensagens, unindo o separador ao conteúdo subsequente
    if len(parts) > 1:
        # A primeira parte é o primeiro email ou lixo
        if parts[0].strip():
            emails.append(parts[0].strip())
        
        # Itera sobre separadores e conteúdos subsequentes
        for i in range(1, len(parts), 2):
            separator = parts[i]
            content_part = parts[i+1]
            if content_part.strip():
                # Tenta anexar o separador ao conteúdo, se for um header
                emails.append((separator + content_part).strip())
    else:
        # Se não houver divisão, é um único email
        emails = [content]

    # Filtra emails vazios e limpa
    return [email.strip() for email in emails if email.strip()]


def process_email_async(email_content: str, sender: str, service: EmailAnalyzerService, mailer: Optional[EmailSender], config: Any) -> None:
    """Processa email de forma assíncrona para evitar timeouts."""
    try:
        # Análise com IA
        preprocessed = basic_preprocess(email_content)
        result = service.analyze(preprocessed)
        
        # Determina ação
        categoria = result.get("categoria", "N/A")
        atencao = result.get("atencao_humana", "NÃO")
        sugestao = result.get("sugestao_resposta_ou_acao", "N/A")
        
        # Ações automáticas (se SMTP habilitado)
        if mailer and atencao.upper() == "NÃO" and categoria.lower() != "spam":
            response_body = generate_automatic_response(sugestao, categoria, email_content)
            mailer.send(
                to_address=sender,
                subject="Resposta automática - MailMind",
                body=response_body,
            )
            logging.info(f"Resposta automática enviada para {sender}")
        elif mailer and atencao.upper() == "SIM" and config.curator_address:
            forward_body = f"""Email recebido para curadoria humana:

REMETENTE: {sender}
CATEGORIA: {categoria}
RESUMO: {result.get('resumo', 'N/A')}
SUGESTÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{email_content[:500]}..."""
            
            mailer.send(
                to_address=config.curator_address,
                subject=f"Encaminhamento para curadoria - {categoria}",
                body=forward_body,
            )
            logging.info(f"Email encaminhado para curadoria: {config.curator_address}")
            
    except Exception as e:
        logging.error(f"Erro no processamento assíncrono: {e}")


def get_mock_email_data() -> dict:
    """Retorna dados mock para testes da interface."""
    return {
        "spam": {
            "sender": "spam@exemplo.com",
            "subject": "Ganhe dinheiro fácil!",
            "content": "Você foi selecionado para ganhar R$ 10.000! Clique aqui agora!"
        },
        "produtivo": {
            "sender": "cliente@empresa.com", 
            "subject": "Proposta de parceria comercial",
            "content": "Gostaríamos de discutir uma possível parceria entre nossas empresas."
        },
        "reclamacao": {
            "sender": "usuario@cliente.com",
            "subject": "Problema com o produto",
            "content": "Estou com dificuldades para usar o produto que comprei."
        }
    }


def analyze_batch_emails(emails: list, service: EmailAnalyzerService, mailer: Optional[EmailSender], config: Any) -> list:
    """Analisa uma lista de emails e retorna os resultados."""
    results = []
    
    for i, email_content in enumerate(emails, 1):
        try:
            sender = extract_sender_from_email(email_content) or 'Não identificado'
            preprocessed = basic_preprocess(email_content)
            result = service.analyze(preprocessed)
            
            # Checagem de sucesso
            if not result or 'categoria' not in result or 'erro' in result:
                raise Exception(f"Falha na análise do Gemini: {result.get('erro', result.get('conteudo', 'Resposta vazia'))}")
            
            # Extrai resultados
            categoria = result.get("categoria", "N/A")
            atencao = result.get("atencao_humana", "N/A")
            resumo = result.get("resumo", "N/A")
            sugestao = result.get("sugestao_resposta_ou_acao", result.get("conteudo", "N/A"))
            
            action_result = "Nenhuma ação automática (SIMULADA)"
            
            if atencao.upper() == "NÃO" and sender != 'Não identificado':
                if categoria.lower() == "spam":
                    action_result = "Nenhuma resposta automática enviada (spam detectado)"
                else:
                    response_body = generate_automatic_response(sugestao, categoria, email_content, sender)
                    
                    if mailer:
                        mailer.send(to_address=sender, subject="Resposta automática - MailMind", body=response_body)
                        action_result = f"Resposta automática ENVIADA para {sender}"
                    else:
                        action_result = f"[SIMULAÇÃO] Resposta seria enviada para {sender}"
                        
            elif atencao.upper() == "SIM":
                forward_body = f"""Email {i}/{len(emails)} recebido para curadoria humana:
REMETENTE: {sender}
CATEGORIA: {categoria}
RESUMO: {resumo}
SUGESTÃO/AÇÃO: {sugestao}
--- CONTEÚDO ORIGINAL ---
{email_content[:300]}...

Este email foi automaticamente encaminhado pelo sistema MailMind."""
                
                if mailer:
                    mailer.send(to_address=config.curator_address, subject=f"Encaminhamento para curadoria - {categoria} (Email {i}/{len(emails)})", body=forward_body)
                    action_result = f"ENVIADO para CURADORIA HUMANA ({config.curator_address})"
                else:
                    action_result = f"[SIMULAÇÃO] Seria encaminhado para curadoria"
            
            results.append({
                'email_number': i,
                'sender': sender,
                'categoria': categoria,
                'atencao_humana': atencao,
                'resumo': resumo,
                'sugestao': sugestao,
                'action_result': action_result,
                'content_preview': email_content[:200] + "..." if len(email_content) > 200 else email_content
            })
            
        except Exception as e:
            logging.error(f"Erro fatal ao analisar email {i}: {e}", exc_info=True)
            results.append({
                'email_number': i,
                'sender': sender,
                'categoria': 'ERRO FATAL',
                'atencao_humana': 'ERRO',
                'resumo': f'Erro na análise: {e}',
                'sugestao': 'Verificar logs e conteúdo.',
                'action_result': f'Falha na análise: {e}',
                'content_preview': email_content[:200] + "..." if len(email_content) > 200 else email_content
            })
    
    return results


def create_app() -> Flask:
    # --- Configuração Inicial ---
    load_dotenv()
    config = load_config()
    
    # 1. Configuração do Gemini Client (API Key e Modelo)
    client = GeminiClient(api_key=config.gemini_api_key, model_name=config.model_name)
    service = EmailAnalyzerService(client=client)
    
    # 2. Configuração do Mailer (SMTP) - Lógica de Fallback
    # Controle de modo SMTP via variável de ambiente
    smtp_enabled = os.getenv("SMTP_ENABLED", "true").lower() == "true"
    mailer = None
    
    # Tentativa 1: SendGrid SMTP (apenas se SMTP habilitado)
    if smtp_enabled:
        sendgrid_host = os.getenv("SMTP_HOST", "")
        sendgrid_port = int(os.getenv("SMTP_PORT", "587"))
        sendgrid_user = os.getenv("SMTP_USER", "")
        sendgrid_password = os.getenv("SMTP_PASSWORD", "")
        noreply_address = os.getenv("NOREPLY_ADDRESS", "")
        
        if all([sendgrid_host, sendgrid_port, sendgrid_user, sendgrid_password, noreply_address]):
            try:
                mailer = EmailSender(host=sendgrid_host, port=sendgrid_port, username=sendgrid_user, password=sendgrid_password, default_from=noreply_address)
            except Exception as e:
                logging.warning(f"SendGrid SMTP falhou: {e}")
                mailer = None
    
    # Tentativa 2: Gmail SMTP (fallback) - apenas se SMTP habilitado
    if smtp_enabled and mailer is None:
        gmail_host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
        gmail_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
        gmail_user = os.getenv("GMAIL_SMTP_USER", "")
        gmail_password = os.getenv("GMAIL_SMTP_PASSWORD", "")
        
        if gmail_user and gmail_password:
            try:
                # Usar noreply_address como default_from se SendGrid falhou mas a variável existe
                default_from = noreply_address if noreply_address else gmail_user
                mailer = EmailSender(host=gmail_host, port=gmail_port, username=gmail_user, password=gmail_password, default_from=default_from)
            except Exception as e:
                logging.warning(f"Gmail SMTP falhou: {e}")
                mailer = None
    
    # Modo simulação se ambos falharem
    if mailer is None:
        if not smtp_enabled:
            logging.info("SMTP desabilitado via SMTP_ENABLED=false - modo simulação ativado")
        else:
            logging.warning("Nenhum SMTP configurado - modo simulação ativado")

    # Configuração de logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    app = Flask(__name__)
    app.secret_key = os.getenv("APP_SECRET", "dev-secret")

    # --- Rotas Principais ---
    
    @app.route("/", methods=["GET"]) 
    def index():
        return send_from_directory('static', 'index.html')
    
    @app.route("/webhook/email", methods=["POST"])
    def webhook_email():
        """Webhook para receber emails automaticamente."""
        try:
            # Tenta ler o conteúdo de email do corpo da requisição (JSON/form)
            if request.is_json:
                data = request.get_json()
                email_content = data.get('email_content', data.get('content', ''))
                sender = data.get('sender', '')
                subject = data.get('subject', '')
            else:
                email_content = request.form.get('email_content', '')
                sender = request.form.get('sender', '')
                subject = request.form.get('subject', '')

            # Constrói o email no formato padrão para extração de remetente
            formatted_email = f"""From: {sender}\nSubject: {subject}\n\n{email_content}"""
            
            if not email_content:
                return jsonify({"error": "Email content is required"}), 400
            
            # Processa o email automaticamente (lote ou individual)
            emails = split_multiple_emails(formatted_email)
            results = analyze_batch_emails(emails, service, mailer, config)
            
            if len(emails) > 1:
                return jsonify({
                    "status": "success",
                    "message": f"Processados {len(emails)} emails automaticamente",
                    "results": results,
                    "batch_mode": True
                })
            else:
                # Se for email único, retorna o primeiro resultado
                result = results[0] if results else {"error": "Failed to analyze single email."}
                if "ERRO" in result.get('categoria', ''):
                    return jsonify({"status": "error", "message": result['resumo'], "result": result}), 500
                
                return jsonify({
                    "status": "success",
                    "message": "Email processado automaticamente via webhook",
                    "result": {
                        "categoria": result.get("categoria"),
                        "atencao_humana": result.get("atencao_humana"),
                        "resumo": result.get("resumo"),
                        "sugestao": result.get("sugestao"),
                        "action_result": result.get("action_result"),
                        "sender": result.get("sender")
                    }
                })
                
        except Exception as e:
            logging.error(f"Erro no webhook: {e}", exc_info=True)
            return jsonify({"error": f"Erro interno: {str(e)}", "trace": str(e)}), 500

    @app.route("/webhook/test", methods=["GET", "POST"])
    def webhook_test():
        """Página de teste para o webhook."""
        if request.method == "GET":
            return send_from_directory('static', 'index.html')
        
        # POST - Simula chamada do webhook, reutilizando webhook_email
        return webhook_email()

    @app.route("/analyze", methods=["POST"]) 
    def analyze():
        """Rota principal para análise de emails via interface web - ANÁLISE SÍNCRONA + SMTP ASSÍNCRONO."""
        raw_text, origin = read_text_from_upload()
        if not raw_text:
            if origin == "file_too_large":
                return jsonify({"error": "📁 Arquivo muito grande. Limite de 2MB."}), 400
            return jsonify({"error": "📝 Envie um arquivo .txt/.pdf ou cole o texto do e-mail."}), 400

        # Detecta se há múltiplos emails no arquivo
        emails = split_multiple_emails(raw_text)
        
        if len(emails) > 1:
            # Análise em lote - múltiplos emails
            results = []
            for email_content in emails:
                try:
                    sender = extract_sender_from_email(email_content) or 'Não identificado'
                    preprocessed = basic_preprocess(email_content)
                    result = service.analyze(preprocessed)
                    
                    # Determina categoria e ação
                    categoria = result.get("categoria", "N/A")
                    atencao = result.get("atencao_humana", "NÃO")
                    resumo = result.get("resumo", "N/A")
                    sugestao = result.get("sugestao_resposta_ou_acao", "N/A")
                    
                    # Inicia SMTP em background (se habilitado)
                    if mailer:
                        threading.Thread(
                            target=process_email_async, 
                            args=(email_content, sender, service, mailer, config)
                        ).start()
                    
                    # Determina mensagem de ação baseada na categoria
                    if atencao.upper() == "SIM":
                        acao_msg = "📧 Será encaminhado para curadoria humana" if mailer else "📧 [SIMULAÇÃO] Seria encaminhado para curadoria"
                    elif categoria.lower() == "spam":
                        acao_msg = "🚫 Spam detectado - nenhuma ação necessária"
                    else:
                        acao_msg = "🤖 Resposta automática será enviada" if mailer else "🤖 [SIMULAÇÃO] Resposta automática seria enviada"
                    
                    results.append({
                        "categoria": categoria,
                        "atencao_humana": atencao,
                        "resumo": resumo,
                        "sugestao": sugestao,
                        "sender": sender,
                        "acao": acao_msg
                    })
                except Exception as e:
                    results.append({
                        "categoria": "❌ ERRO",
                        "atencao_humana": "NÃO",
                        "resumo": f"Falha na análise: {str(e)[:100]}...",
                        "sugestao": "Verifique o conteúdo do email e tente novamente",
                        "sender": "Não identificado",
                        "acao": "⚠️ Erro no processamento - análise manual necessária"
                    })
            
            return jsonify({
                "total_emails": len(emails),
                "results": results,
                "message": f"✅ Análise concluída para {len(emails)} email(s)"
            })
        else:
            # Análise individual - email único
            try:
                sender = extract_sender_from_email(raw_text) or 'Não identificado'
                preprocessed = basic_preprocess(raw_text)
                result = service.analyze(preprocessed)
                
                # Verifica se a análise foi bem-sucedida
                if not result or 'categoria' not in result:
                    raise Exception("Falha na análise do Gemini")
                
                # Determina categoria e ação
                categoria = result.get("categoria", "N/A")
                atencao = result.get("atencao_humana", "NÃO")
                resumo = result.get("resumo", "N/A")
                sugestao = result.get("sugestao_resposta_ou_acao", "N/A")
                
                # Inicia SMTP em background (se habilitado)
                if mailer:
                    threading.Thread(
                        target=process_email_async, 
                        args=(raw_text, sender, service, mailer, config)
                    ).start()
                    
                    # Determina mensagem de ação baseada na categoria
                    if atencao.upper() == "SIM":
                        acao = "📧 Será encaminhado para curadoria humana"
                    elif categoria.lower() == "spam":
                        acao = "🚫 Spam detectado - nenhuma ação necessária"
                    else:
                        acao = "🤖 Resposta automática será enviada"
                else:
                    if atencao.upper() == "SIM":
                        acao = "📧 [SIMULAÇÃO] Seria encaminhado para curadoria"
                    elif categoria.lower() == "spam":
                        acao = "🚫 Spam detectado - nenhuma ação necessária"
                    else:
                        acao = "🤖 [SIMULAÇÃO] Resposta automática seria enviada"
                
                return jsonify({
                    "categoria": categoria,
                    "atencao_humana": atencao,
                    "resumo": resumo,
                    "sugestao": sugestao,
                    "acao": acao,
                    "sender": sender
                })
                
            except Exception as e:
                logging.error(f"Erro na análise: {e}")
                return jsonify({
                    "error": "❌ Erro interno do servidor",
                    "details": f"Falha na análise: {str(e)[:200]}...",
                    "sugestao": "Tente novamente ou verifique o conteúdo do email"
                }), 500

    @app.route("/test/<test_type>")
    def test_mock(test_type):
        """Rota para testar com dados mock."""
        try:
            mock_data = get_mock_email_data()
            
            if test_type not in mock_data:
                return jsonify({
                    "error": f"❌ Tipo de teste inválido. Use: {', '.join(mock_data.keys())}",
                    "available_types": list(mock_data.keys())
                }), 400
            
            data = mock_data[test_type]
            
            # Simula o processamento (individual)
            preprocessed = basic_preprocess(data["content"])
            result = service.analyze(preprocessed) # Chama o service
            
            # Simula as ações automáticas
            categoria = result.get("categoria", "N/A")
            atencao = result.get("atencao_humana", "N/A")
            resumo = result.get("resumo", "N/A")
            sugestao = result.get("sugestao_resposta_ou_acao", result.get("conteudo", "N/A"))
            
            extracted_sender = extract_sender_from_email(data["content"])
            sender_email = extracted_sender or data["sender"] # Usa o sender do mock se falhar

            # Lógica de ação consolidada
            action_result = "Nenhuma ação executada"
            if atencao.upper() == "NÃO":
                if categoria.lower() != "spam":
                    response_body = generate_automatic_response(sugestao, categoria, data["content"])
                    if mailer:
                        mailer.send(to_address=sender_email, subject="Resposta automática - MailMind", body=response_body)
                        action_result = f" Resposta automática ENVIADA para o REMETENTE ({sender_email})"
                    else:
                        action_result = f" [SIMULAÇÃO] Resposta automática seria enviada para o REMETENTE ({sender_email})"
            elif atencao.upper() == "SIM":
                forward_body = f"""Email recebido para curadoria humana:

REMETENTE: {sender_email}
CATEGORIA: {categoria}
RESUMO: {resumo}
SUGESTÃO/AÇÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{data['content'][:500]}...

Este email foi automaticamente encaminhado pelo sistema MailMind."""
                if mailer:
                    mailer.send(to_address=config.curator_address, subject=f"Encaminhamento para curadoria - {categoria}", body=forward_body)
                    action_result = f" ENVIADO para CURADORIA HUMANA ({config.curator_address})"
                else:
                    action_result = f" [SIMULAÇÃO] Seria encaminhado para CURADORIA HUMANA ({config.curator_address})"
        
            return jsonify({
                "categoria": categoria,
                "atencao_humana": atencao,
                "resumo": resumo,
                "sugestao": sugestao,
                "acao_executada": action_result,
                "test_mode": True,
                "test_type": test_type,
                "sender_email": sender_email
            })
            
        except Exception as e:
            logging.error(f"Erro no teste mock: {e}", exc_info=True)
            return jsonify({
                "error": "❌ Erro no teste",
                "details": f"Falha no processamento: {str(e)[:200]}...",
                "test_type": test_type
            }), 500

    # Rotas de Health Check e Mock Data
    @app.route('/health')
    def health():
        """Endpoint de health check para monitoramento"""
        return jsonify({
            'status': 'healthy',
            'message': 'MailMind está funcionando corretamente',
            'version': '1.0.0'
        })
    
    @app.route('/mock_data')
    def mock_data():
        """Endpoint para retornar dados mock para testes de UI"""
        return jsonify(get_mock_email_data())


    # Rotas para servir arquivos estáticos (sem alterações)
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory('static', filename)

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory('static/assets', filename)

    @app.route('/docs/<path:filename>')
    def serve_docs(filename):
        return send_from_directory('../docs', filename)

    # Rota catch-all para SPA (sem alterações)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        # Lista de prefixes que NÃO devem servir o React App
        api_prefixes = ['api/', 'webhook/', 'test/', 'analyze', 'health', 'static/', 'docs/', 'mock_data']
        if any(path.startswith(prefix) for prefix in api_prefixes):
            return jsonify({'error': 'Not found'}), 404
        
        return send_from_directory('static', 'index.html')

    return app


# Exportar app para gunicorn/Hypercorn
app = create_app()

def main():
    """Função principal para executar a aplicação."""
    port = int(os.getenv("PORT", 8001))
    print(f"Iniciando MailMind em http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()