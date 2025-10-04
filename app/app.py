import io
import os
import json
import logging
from typing import Tuple
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory, jsonify
from dotenv import load_dotenv
from pdfminer.high_level import extract_text

from .config import load_config
from .providers.gemini_client import GeminiClient
from .services.email_analyzer import EmailAnalyzerService
from .utils.text_preprocess import basic_preprocess
from .utils.email_sender import EmailSender


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

    filename = file.filename.lower()
    data = file.read()

    if filename.endswith(".txt"):
        return data.decode("utf-8", errors="ignore"), "txt"
    if filename.endswith(".pdf"):
        with io.BytesIO(data) as buf:
            text = extract_text(buf)
            if text:
                # Melhor limpeza do texto PDF
                # Primeiro, preserva quebras de linha que podem ser importantes para separar emails
                lines = text.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    # Remove espaços extras mas preserva a linha se não estiver vazia
                    cleaned_line = ' '.join(line.split())
                    if cleaned_line.strip():
                        cleaned_lines.append(cleaned_line)
                
                # Reconstrói o texto preservando estrutura
                cleaned_text = '\n'.join(cleaned_lines)
                
                # Se o texto está muito fragmentado, tenta uma abordagem diferente
                if len(cleaned_text.split()) < 20:  # Muito poucas palavras
                    # Tentar extrair texto de forma mais agressiva
                    words = text.replace('\n', ' ').replace('\r', ' ').split()
                    reconstructed = []
                    for word in words:
                        # Remove caracteres especiais mas mantém palavras válidas
                        clean_word = ''.join(c for c in word if c.isalnum() or c in '@.-_')
                        if len(clean_word) > 1:  # Ignorar caracteres únicos
                            reconstructed.append(clean_word)
                    cleaned_text = ' '.join(reconstructed)
                
                # Se ainda estiver muito curto, usar fallback mais informativo
                if len(cleaned_text.strip()) < 30:
                    cleaned_text = f"Conteúdo PDF extraído com dificuldade. Texto original: {text[:200]}..."
                
                # PDF extraído com sucesso
                return cleaned_text, "pdf"
        return "", "pdf"

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


def generate_automatic_response(sugestao, categoria, email_content, sender_email=""):
    """Gera uma resposta automática personalizada usando IA"""
    try:
        from .services.email_analyzer import EmailAnalyzerService
        from .providers.gemini_client import GeminiClient
        from .config import load_config
        
        config = load_config()
        client = GeminiClient(api_key=config.gemini_api_key, model_name=config.model_name)
        
        # Extrai o nome do sender do email se disponível
        sender_name = ""
        if sender_email:
            # Tenta extrair nome do email (parte antes do @)
            sender_name = sender_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        
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
        3. **RESPOSTA CONTEXTUAL**: Baseie sua resposta na categoria específica:
           - Para "Felicitação": Agradeça pelos elogios e reconhecimento
           - Para "Mensagem Geral": Agradeça pelo contato e interesse
           - Para "Marketing Genérico": Agradeça mas indique que não é relevante
        4. **ORIENTAÇÃO CLARA**: Indique que não requer atenção imediata da equipe
        5. **CANAL ALTERNATIVO**: Sugira contato através dos canais oficiais se necessário
        6. **INSTRUÇÃO IMPORTANTE**: Inclua "Esta é uma resposta automática gerada pelo nosso sistema de análise de emails, por favor, não responda para este endereço."
        7. **ASSINATURA**: Termine com "Atenciosamente, Equipe MailMind"

        FORMATO DA RESPOSTA:
        - Use parágrafos bem estruturados
        - Mantenha tom profissional mas caloroso
        - Seja específico baseado no conteúdo recebido
        - Não inclua aspas ou formatação especial
        - A resposta deve estar pronta para envio direto

        Gere uma resposta completa e personalizada agora:
        """
        
        # Gerando resposta automática
        
        
        response = client.generate_content(prompt)
        
        # Verifica diferentes estruturas de resposta
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        elif response and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                return candidate.content.parts[0].text.strip()
        else:
            # Fallback: retorna mensagem genérica se a IA falhar
            return "Obrigado pelo contato. Sua mensagem foi recebida e será analisada pela nossa equipe."
            
    except Exception as e:
        logging.error(f"Erro ao gerar resposta automática: {e}")
        logging.error(f"Tipo de erro: {type(e).__name__}")
        
        # Fallback para resposta padrão em caso de erro
        return "Obrigado pelo contato. Sua mensagem foi recebida e será analisada pela nossa equipe."


def split_multiple_emails(content: str) -> list:
    """Divide um arquivo com múltiplos emails em uma lista de emails individuais."""
    import re
    
    # Padrões para identificar início de novos emails (mais flexíveis para PDFs)
    email_separators = [
        # Padrões com quebras de linha duplas
        r'\n\nFrom:\s+[^\n]+@[^\n]+\.[^\n]+',  # From: email@domain.com
        r'\n\nDe:\s+[^\n]+@[^\n]+\.[^\n]+',   # De: email@domain.com
        r'\n\nRemetente:\s+[^\n]+@[^\n]+\.[^\n]+',  # Remetente: email@domain.com
        r'\n\nSender:\s+[^\n]+@[^\n]+\.[^\n]+',    # Sender: email@domain.com
        
        # Padrões com quebras de linha simples (para PDFs mal formatados)
        r'\nFrom:\s+[^\n]+@[^\n]+\.[^\n]+',  # From: email@domain.com
        r'\nDe:\s+[^\n]+@[^\n]+\.[^\n]+',   # De: email@domain.com
        r'\nRemetente:\s+[^\n]+@[^\n]+\.[^\n]+',  # Remetente: email@domain.com
        r'\nSender:\s+[^\n]+@[^\n]+\.[^\n]+',    # Sender: email@domain.com
        
        # Separadores explícitos
        r'\n\n---\n',  # Separador explícito
        r'\n\n===\n',  # Separador explícito
        r'\n---\n',    # Separador com uma quebra de linha
        r'\n===\n',    # Separador com uma quebra de linha
        
        # Headers de email
        r'\n\nMessage-ID:\s+<[^>]+>',  # Message-ID: <id>
        r'\nMessage-ID:\s+<[^>]+>',    # Message-ID: <id> (uma quebra)
        r'\n\nDate:\s+\w{3},\s+\d{1,2}\s+\w{3}\s+\d{4}',  # Date completa
        r'\nDate:\s+\w{3},\s+\d{1,2}\s+\w{3}\s+\d{4}',    # Date (uma quebra)
    ]
    
    # Verifica se há múltiplos emails
    separator_count = 0
    for separator in email_separators:
        matches = re.findall(separator, content, re.IGNORECASE)
        separator_count += len(matches)
    
        # Verificando separadores de email
    
    # Se não encontrar separadores suficientes, trata como um único email
    if separator_count == 0:
        # Tratando como email único
        return [content]
    
    # Se encontrar separadores, divide o conteúdo
    emails = [content]
    
    for separator in email_separators:
        if re.search(separator, content, re.IGNORECASE):
            # Dividindo por separador encontrado
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
                    separator_match = re.search(separator, content, re.IGNORECASE)
                    if separator_match:
                        separator_text = separator_match.group()
                        emails.append(separator_text + part.strip())
            break
    
    # Remove emails vazios e limpa
    emails = [email.strip() for email in emails if email.strip()]
    
    # Divisão de emails concluída
    
    # Se só temos um email após a divisão, retorna como lista com um item
    if len(emails) == 1:
        return emails
    
    return emails


def analyze_batch_emails(emails: list, service, mailer, config) -> list:
    """Analisa uma lista de emails e retorna os resultados."""
    results = []
    
    for i, email_content in enumerate(emails, 1):
        try:
            # Analisando email
            
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
                # Verifica se é spam - spam NÃO deve receber resposta automática
                if categoria.lower() == "spam":
                    action_result = " Nenhuma resposta automática foi enviada (spam detectado)"
                else:
                    # Gerar resposta automática personalizada usando IA
                    response_body = generate_automatic_response(sugestao, categoria, email_content, sender)
                    
                    if mailer:
                        mailer.send(
                            to_address=sender,
                            subject="Resposta automática - MailMind",
                            body=response_body,
                        )
                        action_result = f" Resposta automática ENVIADA para {sender}"
                    else:
                        action_result = f" [SIMULAÇÃO] Resposta seria enviada para {sender}"
                    
            elif atencao.upper() == "SIM":
                # Encaminhamento para curadoria
                forward_body = f"""Email {i}/{len(emails)} recebido para curadoria humana:

REMETENTE: {sender or 'Não identificado'}
CATEGORIA: {categoria}
RESUMO: {resumo}

SUGESTÃO/AÇÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{email_content[:300]}...

Este email foi automaticamente encaminhado pelo sistema MailMind."""
                
                if mailer:
                    mailer.send(
                        to_address=config.curator_address,
                        subject=f"Encaminhamento para curadoria - {categoria} (Email {i}/{len(emails)})",
                        body=forward_body,
                    )
                    action_result = f" ENVIADO para CURADORIA HUMANA ({config.curator_address})"
                else:
                    action_result = f" [SIMULAÇÃO] Seria encaminhado para curadoria"
            
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
            logging.error(f" Erro ao analisar email {i}: {e}")
            results.append({
                'email_number': i,
                'sender': 'ERRO',
                'categoria': 'ERRO',
                'atencao_humana': 'ERRO',
                'resumo': f'Erro na análise: {e}',
                'sugestao': 'Verificar manualmente',
                'action_result': f' Falha na análise: {e}',
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
        },
        "felicitacao": {
            "content": """From: cliente@empresa.com
Subject: Parabéns pelo excelente trabalho!

Olá equipe,

Gostaria de parabenizar vocês pelo excelente trabalho realizado este ano. 
A empresa está de parabéns pelos resultados alcançados e pela qualidade 
dos serviços prestados.

Desejamos muito sucesso para os próximos anos e que continuem com esse 
padrão de excelência!

Atenciosamente,
João Silva
Cliente satisfeito""",
            "expected_sender": "cliente@empresa.com",
            "expected_category": "IMPRODUTIVO"
        }
    }


def create_app() -> Flask:
    load_dotenv()
    config = load_config()
    client = GeminiClient(api_key=config.gemini_api_key, model_name=config.model_name)
    service = EmailAnalyzerService(client=client)
    # Sistema de fallback: SendGrid → Gmail SMTP → Simulação
    mailer = None
    
    # Tentativa 1: SendGrid SMTP
    sendgrid_host = os.getenv("SMTP_HOST", "")
    sendgrid_port = int(os.getenv("SMTP_PORT", "587"))
    sendgrid_user = os.getenv("SMTP_USER", "")
    sendgrid_password = os.getenv("SMTP_PASSWORD", "")
    noreply_address = os.getenv("NOREPLY_ADDRESS", "")
    
    if all([sendgrid_host, sendgrid_port, sendgrid_user, sendgrid_password, noreply_address]):
        try:
            mailer = EmailSender(
                host=sendgrid_host,
                port=sendgrid_port,
                username=sendgrid_user,
                password=sendgrid_password,
                default_from=noreply_address,
            )
            logging.info(" SendGrid SMTP configurado")
        except Exception as e:
            logging.warning(f" SendGrid SMTP falhou: {e}")
            mailer = None
    
    # Tentativa 2: Gmail SMTP (fallback)
    if mailer is None:
        gmail_host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
        gmail_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
        gmail_user = os.getenv("GMAIL_SMTP_USER", "")
        gmail_password = os.getenv("GMAIL_SMTP_PASSWORD", "")
        
        if gmail_user and gmail_password:
            try:
                mailer = EmailSender(
                    host=gmail_host,
                    port=gmail_port,
                    username=gmail_user,
                    password=gmail_password,
                    default_from=gmail_user,
                )
                logging.info(" Gmail SMTP configurado (fallback)")
            except Exception as e:
                logging.warning(f" Gmail SMTP falhou: {e}")
                mailer = None
    
    # Modo simulação se ambos falharem
    if mailer is None:
        logging.warning(" Nenhum SMTP configurado - modo simulação ativado")

    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    logging.info(" Configuração carregada com sucesso")

    app = Flask(__name__)
    app.secret_key = os.getenv("APP_SECRET", "dev-secret")

    @app.route("/", methods=["GET"]) 
    def index():
        return send_from_directory('static', 'index.html')
    
    @app.route("/webhook/email", methods=["POST"])
    def webhook_email():
        """Webhook para receber emails automaticamente."""
        try:
            # Tenta receber dados JSON primeiro
            if request.is_json:
                data = request.get_json()
                # Aceita tanto 'email_content' quanto 'content' para compatibilidade
                email_content = data.get('email_content', data.get('content', ''))
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
            
            logging.info(f" Webhook recebeu email de: {sender}")
            
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
                    # Verifica se é spam - spam NÃO deve receber resposta automática
                    if categoria.lower() == "spam":
                        action_result = " Nenhuma resposta automática foi enviada (spam detectado)"
                    else:
                        # Gerar resposta automática personalizada usando IA
                        response_body = generate_automatic_response(sugestao, categoria, email_content, extracted_sender)
                        
                        if mailer:
                            mailer.send(
                                to_address=extracted_sender,
                                subject="Resposta automática - MailMind",
                                body=response_body,
                            )
                            action_result = f" Resposta automática ENVIADA para {extracted_sender}"
                        else:
                            action_result = f" [SIMULAÇÃO] Resposta seria enviada para {extracted_sender}"
                        
                elif atencao.upper() == "SIM":
                    # Encaminhamento para curadoria
                    forward_body = f"""Email recebido via webhook para curadoria humana:

REMETENTE: {extracted_sender}
CATEGORIA: {categoria}
RESUMO: {resumo}

SUGESTÃO/AÇÃO: {sugestao}

--- CONTEÚDO ORIGINAL ---
{formatted_email[:500]}...

Este email foi automaticamente encaminhado pelo sistema MailMind via webhook."""
                    
                    if mailer:
                        mailer.send(
                            to_address=config.curator_address,
                            subject=f"Webhook - Encaminhamento para curadoria - {categoria}",
                            body=forward_body,
                        )
                        action_result = f" ENVIADO para CURADORIA HUMANA ({config.curator_address})"
                    else:
                        action_result = f" [SIMULAÇÃO] Seria encaminhado para curadoria"
                
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
            logging.error(f" Erro no webhook: {e}")
            return {"error": f"Erro interno: {str(e)}"}, 500

    @app.route("/webhook/test", methods=["GET", "POST"])
    def webhook_test():
        """Página de teste para o webhook."""
        if request.method == "GET":
            return send_from_directory('static', 'index.html')
        
        # Teste via POST - pode ser formulário ou JSON
        if request.is_json:
            # JSON direto
            data = request.get_json()
            test_data = {
                "sender": data.get("sender", "teste@exemplo.com"),
                "subject": data.get("subject", "Teste Webhook"),
                "email_content": data.get("email_content", "Este é um email de teste para o webhook.")
            }
        else:
            # Formulário tradicional
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
            # Verifica se é spam - spam NÃO deve receber resposta automática
            if categoria.lower() == "spam":
                action_result = " Nenhuma resposta automática foi enviada (spam detectado)"
            else:
                # Gerar resposta automática personalizada usando IA
                response_body = generate_automatic_response(sugestao, categoria, data["content"])
                
                if mailer:
                    mailer.send(
                        to_address=sender_email,
                        subject="Resposta automática - Email Analyzer",
                        body=response_body,
                    )
                    action_result = f" Resposta automática ENVIADA para o REMETENTE ({sender_email})"
                else:
                    action_result = f" [SIMULAÇÃO] Resposta automática seria enviada para o REMETENTE ({sender_email}):\n\n{response_body}"
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
                mailer.send(
                    to_address=config.curator_address,
                    subject=f"Encaminhamento para curadoria - {categoria}",
                    body=forward_body,
                )
                action_result = f" ENVIADO para CURADORIA HUMANA ({config.curator_address})"
            else:
                action_result = f" [SIMULAÇÃO] Seria encaminhado para CURADORIA HUMANA ({config.curator_address}):\n\n{forward_body}"
        else:
            action_result = " Categoria não identificada"
        
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

    @app.route("/analyze", methods=["POST"]) 
    def analyze():
        raw_text, origin = read_text_from_upload()
        if not raw_text:
            return jsonify({"error": "Envie um arquivo .txt/.pdf ou cole o texto do e-mail."}), 400

        # Detecta se há múltiplos emails no arquivo
        emails = split_multiple_emails(raw_text)
        
        if len(emails) > 1:
            # Análise em lote - múltiplos emails
            logging.info(f" Detectados {len(emails)} emails para análise em lote")
            results = analyze_batch_emails(emails, service, mailer, config)
            
            return jsonify({
                "total_emails": len(emails),
                "results": results,
                "batch_mode": True
            })
        else:
            # Análise individual - um email
            preprocessed = basic_preprocess(raw_text)
            try:
                result = service.analyze(preprocessed)
            except ValueError as e:
                if "Resposta inválida do Gemini" in str(e):
                    # Se for PDF e Gemini falhar, retorna análise básica
                    if origin == "pdf":
                        return jsonify({
                            "categoria": "Conteúdo PDF",
                            "atencao_humana": "SIM",
                            "resumo": "Arquivo PDF processado com dificuldade. Requer análise manual.",
                            "sugestao": "Revisar manualmente o conteúdo do PDF para análise adequada.",
                            "acao_executada": " PDF processado - requer análise manual",
                            "origem": origin
                        })
                    # Para outros casos, retorna erro genérico
                    return jsonify({"error": "Erro na análise do email. Tente novamente."}), 500
                else:
                    raise e
            
            # Verifica se a análise foi bem-sucedida
            if not result or 'categoria' not in result:
                # Se for PDF e falhar, retorna análise básica
                if origin == "pdf":
                    return jsonify({
                        "categoria": "Conteúdo PDF",
                        "atencao_humana": "SIM",
                        "resumo": "Arquivo PDF processado com dificuldade. Requer análise manual.",
                        "sugestao": "Revisar manualmente o conteúdo do PDF para análise adequada.",
                        "acao_executada": " PDF processado - requer análise manual",
                        "origem": origin
                    })
                return jsonify({"error": "Erro na análise do email. Tente novamente."}), 500
            
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
                
                # Busca o remetente manual (formulário ou JSON)
                if request.is_json:
                    data = request.get_json()
                    manual_sender = data.get("sender", "")
                else:
                    manual_sender = request.form.get("reply_to", "")
                
                # Usa o remetente extraído automaticamente ou o informado manualmente
                sender_email = extracted_sender or manual_sender
                
                if atencao.upper() == "NÃO":
                    # Verifica se é spam - spam NÃO deve receber resposta automática
                    if categoria.lower() == "spam":
                        action_result = " Nenhuma resposta automática foi enviada (spam detectado)"
                        logging.info(f"Spam detectado - nenhuma resposta enviada para: {sender_email}")
                    else:
                        # Para outros emails IMPRODUTIVOS: responder automaticamente para o REMETENTE ORIGINAL
                        if sender_email:
                            # Gerar resposta automática personalizada usando IA
                            response_body = generate_automatic_response(sugestao, categoria, raw_text)
                        
                            # Tentar enviar com fallback automático
                            email_sent = False
                            try:
                                if mailer:
                                    mailer.send(
                                        to_address=sender_email,
                                        subject="Resposta automática - MailMind",
                                        body=response_body,
                                    )
                                    action_result = f" Resposta automática ENVIADA para o REMETENTE ({sender_email})"
                                    logging.info(f"Email improdutivo detectado - resposta automática enviada para remetente: {sender_email}")
                                    email_sent = True
                            except Exception as e:
                                logging.warning(f"Falha no envio principal: {e}")
                                # Tentar fallback Gmail SMTP
                                try:
                                    gmail_host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
                                    gmail_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
                                    gmail_user = os.getenv("GMAIL_SMTP_USER", "")
                                    gmail_password = os.getenv("GMAIL_SMTP_PASSWORD", "")
                                    
                                    if gmail_user and gmail_password:
                                        fallback_mailer = EmailSender(
                                            host=gmail_host,
                                            port=gmail_port,
                                            username=gmail_user,
                                            password=gmail_password,
                                            default_from=noreply_address,
                                        )
                                        fallback_mailer.send(
                                            to_address=sender_email,
                                            subject="Resposta automática - MailMind",
                                            body=response_body,
                                        )
                                        action_result = f" Resposta automática ENVIADA via Gmail SMTP para o REMETENTE ({sender_email})"
                                        logging.info(f"Email improdutivo detectado - resposta automática enviada via Gmail SMTP para remetente: {sender_email}")
                                        email_sent = True
                                except Exception as fallback_error:
                                    logging.error(f"Falha no fallback Gmail SMTP: {fallback_error}")
                            
                            if not email_sent:
                                action_result = f" [SIMULAÇÃO] Resposta automática seria enviada para o REMETENTE ({sender_email}):\n\n{response_body}"
                                logging.info(f"Email improdutivo detectado - modo simulação (SMTP não configurado)")
                        else:
                            action_result = f" Email do remetente não identificado - não foi possível enviar resposta automática"
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

Este email foi automaticamente encaminhado pelo sistema MailMind."""
                        
                        # Tentar enviar com fallback automático
                        email_sent = False
                        try:
                            if mailer:
                                mailer.send(
                                    to_address=config.curator_address,
                                    subject=f"Encaminhamento para curadoria - {categoria}",
                                    body=forward_body,
                                )
                                action_result = f" ENVIADO para CURADORIA HUMANA ({config.curator_address})"
                                logging.info(f"Email produtivo detectado - encaminhado para curadoria: {config.curator_address}")
                                email_sent = True
                        except Exception as e:
                            logging.warning(f"Falha no envio principal: {e}")
                            # Tentar fallback Gmail SMTP
                            try:
                                gmail_host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
                                gmail_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
                                gmail_user = os.getenv("GMAIL_SMTP_USER", "")
                                gmail_password = os.getenv("GMAIL_SMTP_PASSWORD", "")
                                
                                if gmail_user and gmail_password:
                                    fallback_mailer = EmailSender(
                                        host=gmail_host,
                                        port=gmail_port,
                                        username=gmail_user,
                                        password=gmail_password,
                                        default_from=noreply_address,
                                    )
                                    fallback_mailer.send(
                                        to_address=config.curator_address,
                                        subject=f"Encaminhamento para curadoria - {categoria}",
                                        body=forward_body,
                                    )
                                    action_result = f" ENVIADO via Gmail SMTP para CURADORIA HUMANA ({config.curator_address})"
                                    logging.info(f"Email produtivo detectado - encaminhado via Gmail SMTP para curadoria: {config.curator_address}")
                                    email_sent = True
                            except Exception as fallback_error:
                                logging.error(f"Falha no fallback Gmail SMTP: {fallback_error}")
                        
                        if not email_sent:
                            action_result = f" [SIMULAÇÃO] Seria encaminhado para CURADORIA HUMANA ({config.curator_address}):\n\n{forward_body}"
                            logging.info(f"Email produtivo detectado - modo simulação (SMTP não configurado)")
            except Exception as e:
                action_result = f" Falha ao enviar e-mail: {e}"
                logging.error(f"Erro no envio de email: {e}")

            return jsonify({
                "categoria": categoria,
                "atencao_humana": atencao,
                "resumo": resumo,
                "sugestao": sugestao,
                "origem": origin,
                "acao_executada": action_result,
            })

    @app.route('/health')
    def health():
        """Endpoint de health check para monitoramento"""
        return jsonify({
            'status': 'healthy',
            'message': 'MailMind está funcionando corretamente',
            'version': '1.0.0'
        })

    # Rotas para servir arquivos estáticos do React
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve arquivos estáticos do React"""
        return send_from_directory('static', filename)

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Serve assets do React (JS, CSS)"""
        return send_from_directory('static/assets', filename)

    @app.route('/docs/<path:filename>')
    def serve_docs(filename):
        """Serve documentação (LGPD, etc.)"""
        return send_from_directory('../docs', filename)

    # Rota catch-all para SPA (Single Page Application) - deve ser a última rota
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react_app(path):
        """Serve a aplicação React para todas as rotas não-API"""
        # Se for uma rota de API, não servir o React
        if path.startswith('api/') or path.startswith('webhook/') or path.startswith('test/') or path.startswith('analyze') or path.startswith('health') or path.startswith('static/') or path.startswith('docs/'):
            return jsonify({'error': 'Not found'}), 404
        
        # Serve o index.html do React
        return send_from_directory('static', 'index.html')

    return app


# Exportar app para gunicorn
app = create_app()

def main():
    """Função principal para executar a aplicação."""
    port = int(os.getenv("PORT", 8001))
    print(f" Iniciando MailMind em http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()


