
import os
import json
import logging
from dotenv import load_dotenv
from app.config import load_config
from app.providers.gemini_client import GeminiClient
from app.services.email_analyzer import EmailAnalyzerService

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
config = load_config()
client = GeminiClient(api_key=config.gemini_api_key, model_name=config.model_name)
service = EmailAnalyzerService(client=client)

def analyze_email(email_content: str):
    """
    Fachada para manter compatibilidade: usa o serviço e retorna JSON string.
    """
    result = service.analyze(email_content)
    return json.dumps(result, ensure_ascii=False)

def run_examples():
    """Executa exemplos de análise de e-mails via CLI."""
    # Example email content (this would come from the ingestion module in a real system)
    emails_para_analisar = {
        "E-mail 1 (Dúvida sobre Transação)": """
        Assunto: Dúvida sobre meu extrato de conta
        Prezados,
        Gostaria de saber por que o valor de R$ 250,00 foi debitado da minha conta no dia 28/09/2025.
        Não reconheço essa transação.
        Por favor, poderiam verificar e me dar um retorno o mais breve possível?
        Atenciosamente,
        João Silva
        """,
        "E-mail 2 (Mensagem Geral)": """
        Assunto: Feliz Natal!
        Olá equipe,
        Só queria desejar um feliz natal e um próspero ano novo a todos!
        Boas festas!
        Abraços,
        Maria Souza
        """,
        "E-mail 3 (Proposta Comercial)": """
        Assunto: Proposta de parceria
        Olá,
        Somos da empresa X e gostaríamos de apresentar uma proposta de parceria para seus serviços.
        Temos certeza que seria mutuamente benéfica. Podemos agendar uma reunião?
        Atenciosamente,
        Carlos Pereira
        """
    }

    for nome_email, conteudo_email in emails_para_analisar.items():
        logging.info("Analisando: %s", nome_email)
        resultado_str = analyze_email(conteudo_email)

        try:
            # Tenta converter a string JSON para um dicionário Python
            analise = json.loads(resultado_str)
            print(f"  - Atenção Humana Necessária: {analise.get('atencao_humana', 'N/A')}")
            print(f"  - Categoria: {analise.get('categoria', 'N/A')}")
            print(f"  - Resumo: {analise.get('resumo', 'N/A')}")
            print(f"  - Sugestão/Ação: {analise.get('sugestao_resposta_ou_acao', 'N/A')}")
        except (json.JSONDecodeError, TypeError):
            # Se a resposta não for um JSON válido (pode ser uma mensagem de erro), imprime diretamente
            logging.error("Falha de JSON: %s", resultado_str)


if __name__ == "__main__":
    run_examples()
