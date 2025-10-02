
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_email(email_content: str):
    """
    Analyzes email content using OpenAI API to classify, summarize, and suggest responses.
    """
    prompt = f"""
    Você é um assistente de IA especializado em análise de e-mails para uma empresa financeira.
    Sua tarefa é analisar o seguinte e-mail e fornecer:
    1. Uma classificação da necessidade de atenção humana (SIM/NÃO).
    2. Uma categoria para o e-mail (e.g., 'Solicitação de Status', 'Informação Geral', 'Reclamação', 'Elogio', 'Spam', 'Outro').
    3. Um resumo conciso do e-mail.
    4. Uma sugestão de resposta automática, se o e-mail não exigir atenção humana. Se exigir atenção humana, sugira uma ação para a equipe humana.

    Formato da saída esperada (JSON):
    {{
        "atencao_humana": "SIM" | "NÃO",
        "categoria": "string",
        "resumo": "string",
        "sugestao_resposta_ou_acao": "string"
    }}

    E-mail para análise:
    ---
    {email_content}
    ---
    """

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash", # Using a supported model for demonstration
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "Você é um assistente útil que gera JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during OpenAI API call: {e}"

if __name__ == "__main__":
    # Example email content (this would come from the ingestion module in a real system)
    example_email_1 = """
    Assunto: Dúvida sobre meu extrato de conta
    Prezados,
    Gostaria de saber por que o valor de R$ 250,00 foi debitado da minha conta no dia 28/09/2025.
    Não reconheço essa transação.
    Por favor, poderiam verificar e me dar um retorno o mais breve possível?
    Atenciosamente,
    João Silva
    """

    example_email_2 = """
    Assunto: Feliz Natal!
    Olá equipe,
    Só queria desejar um feliz natal e um próspero ano novo a todos!
    Boas festas!
    Abraços,
    Maria Souza
    """

    example_email_3 = """
    Assunto: Proposta de parceria
    Olá,
    Somos da empresa X e gostaríamos de apresentar uma proposta de parceria para seus serviços.
    Temos certeza que seria mutuamente benéfica. Podemos agendar uma reunião?
    Atenciosamente,
    Carlos Pereira
    """

    print("\n--- Analisando E-mail 1 ---")
    analysis_1 = analyze_email(example_email_1)
    print(analysis_1)

    print("\n--- Analisando E-mail 2 ---")
    analysis_2 = analyze_email(example_email_2)
    print(analysis_2)

    print("\n--- Analisando E-mail 3 ---")
    analysis_3 = analyze_email(example_email_3)
    print(analysis_3)

