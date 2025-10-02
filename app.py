import io
import os
import json
import logging
from typing import Tuple
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from pdfminer.high_level import extract_text

from config import load_config
from providers.gemini_client import GeminiClient
from services.email_analyzer import EmailAnalyzerService
from utils.text_preprocess import basic_preprocess
from utils.email_sender import EmailSender


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


def create_app() -> Flask:
    load_dotenv()
    config = load_config()
    client = GeminiClient(api_key=config.gemini_api_key, model_name=config.model_name)
    service = EmailAnalyzerService(client=client)
    mailer = EmailSender(
        host=config.smtp_host,
        port=config.smtp_port,
        username=config.smtp_user,
        password=config.smtp_password,
        default_from=config.noreply_address or config.smtp_user,
    )

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

    @app.route("/analyze", methods=["POST"]) 
    def analyze():
        raw_text, origin = read_text_from_upload()
        if not raw_text:
            flash("Envie um arquivo .txt/.pdf ou cole o texto do e-mail.", "warning")
            return redirect(url_for("index"))

        preprocessed = basic_preprocess(raw_text)
        result = service.analyze(preprocessed)
        # result é dict; convertemos para exibição
        categoria = result.get("categoria", "N/A")
        atencao = result.get("atencao_humana", "N/A")
        resumo = result.get("resumo", "N/A")
        sugestao = result.get("sugestao_resposta_ou_acao", result.get("conteudo", "N/A"))

        # Ações automáticas:
        action_result = None
        try:
            if atencao.upper() == "NÃO":
                # Responder automaticamente para endereço informado no formulário (opcional)
                to_reply = request.form.get("reply_to") or config.curator_address
                if to_reply and config.smtp_host:
                    mailer.send(
                        to_address=to_reply,
                        subject="Resposta automática",
                        body=sugestao,
                    )
                    action_result = f"Resposta automática enviada para {to_reply}."
            elif atencao.upper() == "SIM":
                # Encaminhar para curadoria humana
                if config.curator_address and config.smtp_host:
                    mailer.send(
                        to_address=config.curator_address,
                        subject="Encaminhamento para curadoria humana",
                        body=f"Resumo:\n{resumo}\n\nSugestão/Ação:\n{sugestao}",
                    )
                    action_result = f"Encaminhado para curadoria: {config.curator_address}."
        except Exception as e:
            action_result = f"Falha ao enviar e-mail: {e}"

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


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 8001))  # Mudei para 8001 para evitar conflito
    print(f"🚀 Iniciando Email Analyzer em http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)


