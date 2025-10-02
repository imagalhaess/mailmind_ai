import io
import os
import json
import logging
from typing import Tuple
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from pdfminer.high_level import extract_text

from .config import load_config
from .providers.gemini_client import GeminiClient
from .services.email_analyzer import EmailAnalyzerService
from .utils.text_preprocess import basic_preprocess
from .utils.email_sender import EmailSender


def read_text_from_upload() -> Tuple[str, str]:
    """
    Lê o conteúdo do upload suportando .txt/.pdf e também o campo de texto.
    Retorna (conteudo, origem) para logging.
    """
    if request.form.get("email_text"):
        return request.form["email_text"], "text"

    file = request.files.get("email_file")
    if not file or file.filename == "":
        return "", "none"

    filename = file.filename.lower()
    data = file.read()

    if filename.endswith(".txt"):
        return data.decode("utf-8", errors="ignore"), "txt"
    if filename.endswith(".pdf"):
        with io.BytesIO(data) as buf:
            text = extract_text(buf)
        return text, "pdf"

    return "", "unsupported"


def extract_sender_from_email(email_content: str) -> str:
    """Extrai o email do remetente do conteúdo do email."""
    import re
    
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


def split_multiple_emails(content: str) -> list:
    """Divide um arquivo com múltiplos emails em uma lista de emails individuais."""
    import re
    
    # Padrões para identificar início de novos emails
    email_separators = [
        r'\n\nFrom:',
        r'\n\nDe:',
        r'\n\nRemetente:',
        r'\n\nSender:',
        r'\n\n---',
        r'\n\n===',
        r'\n\nMessage-ID:',
        r'\n\nDate:',
    ]
    
    # Se não encontrar separadores, trata como um único email
    emails = [content]
    
    for separator in email_separators:
        if re.search(separator, content, re.IGNORECASE):
            # Divide pelos separadores encontrados
            parts = re.split(separator, content, flags=re.IGNORECASE)
            emails = []
            for i, part in enumerate(parts):
                if i == 0:
                    # Primeira parte
                    if part.strip():
                        emails.append(part.strip())
                else:
                    # Partes subsequentes - adiciona o separador de volta
                    separator_text = re.search(separator, content, re.IGNORECASE).group()
                    emails.append(separator_text + part.strip())
            break
    
    # Remove emails vazios e limpa
    emails = [email.strip() for email in emails if email.strip()]
    
    return emails


def analyze_batch_emails(emails: list, service, mailer, config) -> list:
    """Analisa uma lista de emails e retorna os resultados."""
    results = []
    
    for i, email_content in enumerate(emails, 1):
        try:
            logging.info(f"📧 Analisando email {i}/{len(emails)}")
            
            # Extrai remetente
            sender = extract_sender_from_email(email_content)
            
            # Preprocessa e analisa
            preprocessed = basic_preprocess(email_content)
            result = service.analyze(preprocessed)
            
            # Verifica se a análise foi bem-sucedida
            if not result or 'categoria' not in result:
                raise Exception("Falha na análise do Gemini")
            
            # Determina ação
            categoria = result.get("categoria", "N/A")
            atencao = result.get("atencao_humana", "N/A")
            resumo = result.get("resumo", "N/A")
            sugestao = result.get("sugestao_resposta_ou_acao", result.get("conteudo", "N/A"))
            
            action_result = None
            
            if atencao.upper() == "NÃO" and sender:
                # Resposta automática para spam/improdutivo
                response_body = f"""Olá,

Recebemos sua mensagem e após análise automatizada, identificamos que ela não requer atenção imediata de nossa equipe.

{sugestao}

Esta é uma resposta automática gerada pelo nosso sistema de análise de emails.

Atenciosamente,
Equipe de Atendimento Automatizado
Email Analyzer System"""
                
                if mailer:
                    mailer.send(
                        to_address=sender,
                        subject="Resposta automática - Email Analyzer",
                        body=response_body,
                    )
                    action_result = f"✅ Resposta automática ENVIADA para {sender}"
                else:
                    action_result = f"📧 [SIMULAÇÃO] Resposta seria enviada para {sender}"
                    
            elif atencao.upper() == "SIM":
                # Encaminhamento para curadoria
                forward_body = f"""Email {i}/{len(emails)} recebido para curadoria humana:

REMETENTE: {sender or 'Não identificado'}
CATEGORIA: {categoria}
RESUMO: {resumo}

SUGESTÃO/AÇÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{email_content[:300]}...

Este email foi automaticamente encaminhado pelo sistema Email Analyzer."""
                
                if mailer:
                    mailer.send(
                        to_address=config.curator_address,
                        subject=f"Encaminhamento para curadoria - {categoria} (Email {i}/{len(emails)})",
                        body=forward_body,
                    )
                    action_result = f"✅ ENVIADO para CUADORIA HUMANA ({config.curator_address})"
                else:
                    action_result = f"📧 [SIMULAÇÃO] Seria encaminhado para curadoria"
            
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
            logging.error(f"❌ Erro ao analisar email {i}: {e}")
            results.append({
                'email_number': i,
                'sender': 'ERRO',
                'categoria': 'ERRO',
                'atencao_humana': 'ERRO',
                'resumo': f'Erro na análise: {e}',
                'sugestao': 'Verificar manualmente',
                'action_result': f'❌ Falha na análise: {e}',
                'content_preview': email_content[:200] + "..." if len(email_content) > 200 else email_content
            })
    
    return results


def get_mock_email_data():
    """Retorna dados mock para teste."""
    return {
        "improdutivo": {
            "content": """From: spammer123@fakeemail.com
Subject: URGENTE!!! GANHE DINHEIRO FÁCIL!!!

🔥🔥🔥 OFERTA IMPERDÍVEL 🔥🔥🔥

Você foi selecionado para receber R$ 50.000,00!!!
Clique aqui agora: www.fakesite.com/ganhe-dinheiro

⚠️ ATENÇÃO: Esta oferta expira em 24 horas!!!
⚠️ Não perca esta oportunidade única!!!

Clique AGORA ou você vai se arrepender!!!

---
Esta mensagem foi enviada para 1.000.000 de pessoas.
Se você não quer mais receber, ignore este email.""",
            "expected_sender": "spammer123@fakeemail.com",
            "expected_category": "IMPRODUTIVO"
        },
        "produtivo": {
            "content": """From: parceiro@startup.com
Subject: Proposta de parceria estratégica

Prezados,

Somos uma startup de tecnologia e gostaríamos de propor uma parceria estratégica 
com sua empresa. Temos uma solução inovadora que pode agregar valor ao seu negócio.

Podemos agendar uma reunião para apresentar nossa proposta?

Atenciosamente,
Maria Santos
CEO - TechStartup""",
            "expected_sender": "parceiro@startup.com",
            "expected_category": "PRODUTIVO"
        }
    }


def create_app() -> Flask:
    load_dotenv()
    config = load_config()
    client = GeminiClient(api_key=config.gemini_api_key, model_name=config.model_name)
    service = EmailAnalyzerService(client=client)
    # Usa Gmail SMTP diretamente (mais confiável)
    gmail_host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
    gmail_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
    gmail_user = os.getenv("GMAIL_SMTP_USER", "")
    gmail_password = os.getenv("GMAIL_SMTP_PASSWORD", "")
    
    if gmail_user and gmail_password:
        mailer = EmailSender(
            host=gmail_host,
            port=gmail_port,
            username=gmail_user,
            password=gmail_password,
            default_from=gmail_user,
        )
        logging.info("✅ Gmail SMTP configurado")
    else:
        mailer = None
        logging.warning("❌ Gmail SMTP não configurado - modo simulação ativado")

    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.info("✅ Configuração carregada com sucesso")

    app = Flask(__name__)
    app.secret_key = os.getenv("APP_SECRET", "dev-secret")

    @app.route("/", methods=["GET"]) 
    def index():
        return render_template("index.html")
    
    @app.route("/webhook/email", methods=["POST"])
    def webhook_email():
        """Webhook para receber emails automaticamente."""
        try:
            # Tenta receber dados JSON primeiro
            if request.is_json:
                data = request.get_json()
                email_content = data.get('email_content', '')
                sender = data.get('sender', '')
                subject = data.get('subject', '')
                
                # Constrói o email no formato padrão
                formatted_email = f"""From: {sender}
Subject: {subject}

{email_content}"""
            else:
                # Recebe dados de formulário
                email_content = request.form.get('email_content', '')
                sender = request.form.get('sender', '')
                subject = request.form.get('subject', '')
                
                formatted_email = f"""From: {sender}
Subject: {subject}

{email_content}"""
            
            if not email_content:
                return {"error": "Email content is required"}, 400
            
            logging.info(f"📨 Webhook recebeu email de: {sender}")
            
            # Processa o email automaticamente
            emails = split_multiple_emails(formatted_email)
            
            if len(emails) > 1:
                # Processamento em lote
                results = analyze_batch_emails(emails, service, mailer, config)
                return {
                    "status": "success",
                    "message": f"Processados {len(emails)} emails automaticamente",
                    "results": results
                }
            else:
                # Processamento individual
                preprocessed = basic_preprocess(formatted_email)
                result = service.analyze(preprocessed)
                
                categoria = result.get("categoria", "N/A")
                atencao = result.get("atencao_humana", "N/A")
                resumo = result.get("resumo", "N/A")
                sugestao = result.get("sugestao_resposta_ou_acao", result.get("conteudo", "N/A"))
                
                # Executa ações automáticas
                extracted_sender = extract_sender_from_email(formatted_email) or sender
                action_result = None
                
                if atencao.upper() == "NÃO" and extracted_sender:
                    # Resposta automática para spam/improdutivo
                    response_body = f"""Olá,

Recebemos sua mensagem e após análise automatizada, identificamos que ela não requer atenção imediata de nossa equipe.

{sugestao}

Esta é uma resposta automática gerada pelo nosso sistema de análise de emails.

Atenciosamente,
Equipe de Atendimento Automatizado
Email Analyzer System"""
                    
                    if mailer:
                        mailer.send(
                            to_address=extracted_sender,
                            subject="Resposta automática - Email Analyzer",
                            body=response_body,
                        )
                        action_result = f"✅ Resposta automática ENVIADA para {extracted_sender}"
                    else:
                        action_result = f"📧 [SIMULAÇÃO] Resposta seria enviada para {extracted_sender}"
                        
                elif atencao.upper() == "SIM":
                    # Encaminhamento para curadoria
                    forward_body = f"""Email recebido via webhook para curadoria humana:

REMETENTE: {extracted_sender}
CATEGORIA: {categoria}
RESUMO: {resumo}

SUGESTÃO/AÇÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{formatted_email[:500]}...

Este email foi automaticamente encaminhado pelo sistema Email Analyzer via webhook."""
                    
                    if mailer:
                        mailer.send(
                            to_address=config.curator_address,
                            subject=f"Webhook - Encaminhamento para curadoria - {categoria}",
                            body=forward_body,
                        )
                        action_result = f"✅ ENVIADO para CUADORIA HUMANA ({config.curator_address})"
                    else:
                        action_result = f"📧 [SIMULAÇÃO] Seria encaminhado para curadoria"
                
                return {
                    "status": "success",
                    "message": "Email processado automaticamente via webhook",
                    "result": {
                        "categoria": categoria,
                        "atencao_humana": atencao,
                        "resumo": resumo,
                        "sugestao": sugestao,
                        "action_result": action_result,
                        "sender": extracted_sender
                    }
                }
                
        except Exception as e:
            logging.error(f"❌ Erro no webhook: {e}")
            return {"error": f"Erro interno: {str(e)}"}, 500

    @app.route("/webhook/test", methods=["GET", "POST"])
    def webhook_test():
        """Página de teste para o webhook."""
        if request.method == "GET":
            return render_template("webhook_test.html")
        
        # Teste via POST
        test_data = {
            "sender": request.form.get("sender", "teste@exemplo.com"),
            "subject": request.form.get("subject", "Teste Webhook"),
            "email_content": request.form.get("email_content", "Este é um email de teste para o webhook.")
        }
        
        # Simula chamada do webhook
        response = webhook_email()
        return response

    @app.route("/test/<test_type>")
    def test_mock(test_type):
        """Rota para testar com dados mock."""
        mock_data = get_mock_email_data()
        
        if test_type not in mock_data:
            flash(f"Tipo de teste inválido. Use: {', '.join(mock_data.keys())}", "error")
            return redirect(url_for("index"))
        
        data = mock_data[test_type]
        
        # Simula o processamento
        preprocessed = basic_preprocess(data["content"])
        result = service.analyze(preprocessed)
        
        categoria = result.get("categoria", "N/A")
        atencao = result.get("atencao_humana", "N/A")
        resumo = result.get("resumo", "N/A")
        sugestao = result.get("sugestao_resposta_ou_acao", result.get("conteudo", "N/A"))
        
        # Simula as ações automáticas
        extracted_sender = extract_sender_from_email(data["content"])
        sender_email = extracted_sender or data["expected_sender"]
        
        if atencao.upper() == "NÃO":
            response_body = f"""Olá,

Recebemos sua mensagem e após análise automatizada, identificamos que ela não requer atenção imediata de nossa equipe.

{sugestao}

Esta é uma resposta automática gerada pelo nosso sistema de análise de emails.

Atenciosamente,
Equipe de Atendimento Automatizado
Email Analyzer System"""
            
            if mailer:
                mailer.send(
                    to_address=sender_email,
                    subject="Resposta automática - Email Analyzer",
                    body=response_body,
                )
                action_result = f"✅ Resposta automática ENVIADA para o REMETENTE ({sender_email})"
            else:
                action_result = f"📧 [SIMULAÇÃO] Resposta automática seria enviada para o REMETENTE ({sender_email}):\n\n{response_body}"
        elif atencao.upper() == "SIM":
            forward_body = f"""Email recebido para curadoria humana:

REMETENTE: {sender_email}
CATEGORIA: {categoria}
RESUMO: {resumo}

SUGESTÃO/AÇÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{data['content'][:500]}...

Este email foi automaticamente encaminhado pelo sistema Email Analyzer."""
            
            if mailer:
                mailer.send(
                    to_address=config.curator_address,
                    subject=f"Encaminhamento para curadoria - {categoria}",
                    body=forward_body,
                )
                action_result = f"✅ ENVIADO para CUADORIA HUMANA ({config.curator_address})"
            else:
                action_result = f"📧 [SIMULAÇÃO] Seria encaminhado para CUADORIA HUMANA ({config.curator_address}):\n\n{forward_body}"
        else:
            action_result = "❓ Categoria não identificada"
        
        return render_template(
            "result.html",
            categoria=categoria,
            atencao_humana=atencao,
            resumo=resumo,
            sugestao=sugestao,
            action_result=action_result,
            test_mode=True,
            test_type=test_type,
            sender_email=sender_email
        )

    @app.route("/analyze", methods=["POST"]) 
    def analyze():
        raw_text, origin = read_text_from_upload()
        if not raw_text:
            flash("Envie um arquivo .txt/.pdf ou cole o texto do e-mail.", "warning")
            return redirect(url_for("index"))

        # Detecta se há múltiplos emails no arquivo
        emails = split_multiple_emails(raw_text)
        
        if len(emails) > 1:
            # Análise em lote - múltiplos emails
            logging.info(f"📁 Detectados {len(emails)} emails para análise em lote")
            results = analyze_batch_emails(emails, service, mailer, config)
            
            return render_template(
                "batch_result.html",
                total_emails=len(emails),
                results=results,
                batch_mode=True
            )
        else:
            # Análise individual - um email
            preprocessed = basic_preprocess(raw_text)
            result = service.analyze(preprocessed)
            
            # Verifica se a análise foi bem-sucedida
            if not result or 'categoria' not in result:
                flash("Erro na análise do email. Tente novamente.", "error")
                return redirect(url_for("index"))
            
            # result é dict; convertemos para exibição
            categoria = result.get("categoria", "N/A")
            atencao = result.get("atencao_humana", "N/A")
            resumo = result.get("resumo", "N/A")
            sugestao = result.get("sugestao_resposta_ou_acao", result.get("conteudo", "N/A"))

            # Ações automáticas:
            action_result = None
            try:
                # Extrai o remetente automaticamente do conteúdo do email
                extracted_sender = extract_sender_from_email(raw_text)
                manual_sender = request.form.get("reply_to", "")
                
                # Usa o remetente extraído automaticamente ou o informado manualmente
                sender_email = extracted_sender or manual_sender
                
                if atencao.upper() == "NÃO":
                    # Para emails IMPRODUTIVOS: responder automaticamente para o REMETENTE ORIGINAL
                    if sender_email:
                        # Conteúdo mais detalhado da resposta automática
                        response_body = f"""Olá,

Recebemos sua mensagem e após análise automatizada, identificamos que ela não requer atenção imediata de nossa equipe.

{sugestao}

Esta é uma resposta automática gerada pelo nosso sistema de análise de emails.

Atenciosamente,
Equipe de Atendimento Automatizado
Email Analyzer System"""
                        
                        if mailer:
                            # ENVIO REAL: Resposta automática vai para quem enviou o email
                            mailer.send(
                                to_address=sender_email,
                                subject="Resposta automática - Email Analyzer",
                                body=response_body,
                            )
                            action_result = f"✅ Resposta automática ENVIADA para o REMETENTE ({sender_email})"
                            logging.info(f"Email improdutivo detectado - resposta automática enviada para remetente: {sender_email}")
                        else:
                            action_result = f"📧 [SIMULAÇÃO] Resposta automática seria enviada para o REMETENTE ({sender_email}):\n\n{response_body}"
                            logging.info(f"Email improdutivo detectado - modo simulação (SMTP não configurado)")
                    else:
                        action_result = f"❌ Email do remetente não identificado - não foi possível enviar resposta automática"
                elif atencao.upper() == "SIM":
                    # Para emails PRODUTIVOS: encaminhar para curadoria humana
                    if config.curator_address:
                        # Conteúdo mais detalhado do encaminhamento
                        forward_body = f"""Email recebido para curadoria humana:

REMETENTE: {sender_email or 'Não identificado'}
CATEGORIA: {categoria}
RESUMO: {resumo}

SUGESTÃO/AÇÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{raw_text[:500]}...

Este email foi automaticamente encaminhado pelo sistema Email Analyzer."""
                        
                        if mailer:
                            # ENVIO REAL: Encaminhamento para curadoria
                            mailer.send(
                                to_address=config.curator_address,
                                subject=f"Encaminhamento para curadoria - {categoria}",
                                body=forward_body,
                            )
                            action_result = f"✅ ENVIADO para CUADORIA HUMANA ({config.curator_address})"
                            logging.info(f"Email produtivo detectado - encaminhado para curadoria: {config.curator_address}")
                        else:
                            action_result = f"📧 [SIMULAÇÃO] Seria encaminhado para CUADORIA HUMANA ({config.curator_address}):\n\n{forward_body}"
                            logging.info(f"Email produtivo detectado - modo simulação (SMTP não configurado)")
            except Exception as e:
                action_result = f"❌ Falha ao enviar e-mail: {e}"
                logging.error(f"Erro no envio de email: {e}")

            return render_template(
                "result.html",
                categoria=categoria,
                atencao_humana=atencao,
                resumo=resumo,
                sugestao=sugestao,
                origem=origin,
                action_result=action_result,
            )

    return app


def main():
    """Função principal para executar a aplicação."""
    app = create_app()
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Iniciando Email Analyzer em http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()


