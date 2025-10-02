# Arquitetura do Sistema de Análise e Curadoria de E-mails

## Visão Geral

Este projeto implementa um sistema de análise e curadoria de e-mails que utiliza uma API de IA Generativa (Google Gemini) para classificar mensagens, resumir seu conteúdo e sugerir respostas automáticas ou ações. O objetivo é otimizar o processo de triagem de e-mails, liberando a equipe para focar em tarefas mais complexas.

## Arquitetura do Sistema

O sistema é composto pelos seguintes módulos principais:

*   **Módulo de Ingestão de E-mails:** Responsável por receber e-mails de uma caixa de entrada designada (não implementado neste protótipo, mas pode ser integrado via IMAP/POP3 ou Webhooks).
*   **Módulo de Pré-processamento:** Prepara o conteúdo do e-mail para análise, extraindo texto puro e removendo elementos irrelevantes.
*   **Módulo de Análise com IA:** Interage com a API do Google Gemini para classificar o e-mail, gerar um resumo e sugerir uma resposta/ação.
*   **Módulo de Classificação e Decisão:** Interpreta a saída da IA para determinar se o e-mail exige atenção humana ou pode ser respondido automaticamente.
*   **Módulo de Respostas Automáticas:** Gera e envia respostas automáticas com base nas sugestões da IA (não implementado neste protótipo, mas pode ser integrado via SMTP).

Para uma descrição mais detalhada da arquitetura, consulte este documento.

## Configuração do Ambiente

Para configurar e executar este projeto, siga os passos abaixo:

### Pré-requisitos

*   Python 3.10+
*   Uma chave de API do Google Gemini

### Instalação

1.  **Clone o repositório (ou crie a estrutura de pastas):**

    ```bash
    mkdir email_analyzer
    cd email_analyzer
    ```

2.  **Crie um ambiente virtual (recomendado):**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # No Linux/macOS
    # .venv\Scripts\activate   # No Windows
    ```

3.  **Instale as dependências:**

    ```bash
    pip install python-dotenv google-generativeai
    ```

4.  **Configure sua chave de API do Google Gemini:**

    Crie um arquivo `.env` na raiz do diretório `email_analyzer` com o seguinte conteúdo, substituindo `SUA_CHAVE_GEMINI_AQUI` pela sua chave real:

    ```
    GEMINI_API_KEY='SUA_CHAVE_GEMINI_AQUI'
    ```

## Uso

O script `main.py` contém a lógica principal para analisar e-mails de exemplo. Para executá-lo:

```bash
python main.py
```

O script irá processar os e-mails de exemplo definidos internamente e imprimir a análise gerada pela IA no console.

## Exemplo de Saída

Para um e-mail que requer atenção humana:

```json
{
    "atencao_humana": "SIM",
    "categoria": "Dúvida sobre Transação",
    "resumo": "O cliente João Silva questiona um débito de R$ 250,00 realizado em 28/09/2025, alegando não reconhecer a transação e solicitando verificação.",
    "sugestao_resposta_ou_acao": "Encaminhar para a equipe de atendimento ao cliente/fraude para investigar a transação de R$ 250,00 debitada em 28/09/2025 e entrar em contato com o cliente João Silva para esclarecimentos."
}
```

Para um e-mail que pode ser respondido automaticamente:

```json
{
    "atencao_humana": "NÃO",
    "categoria": "Informação Geral",
    "resumo": "Maria Souza enviou uma mensagem de Feliz Natal e próspero Ano Novo para a equipe.",
    "sugestao_resposta_ou_acao": "Prezado(a) Maria Souza,\n\nAgradecemos imensamente sua mensagem e desejamos a você também um Feliz Natal e um próspero Ano Novo!\n\nBoas festas!\n\nAtenciosamente,\n[Nome da Equipe/Empresa]"
}
```

## Boas Práticas e Clean Code

Este projeto segue princípios de boas práticas de programação e Clean Code, incluindo:

*   **Modularização:** O código é dividido em funções lógicas para facilitar a manutenção e o entendimento.
*   **Nomenclatura Clara:** Variáveis, funções e classes são nomeadas de forma descritiva.
*   **Comentários e Docstrings:** Funções importantes contêm docstrings explicando seu propósito, argumentos e retorno.
*   **Tratamento de Erros:** Inclui blocos `try-except` para lidar com possíveis falhas na comunicação com a API.
*   **Configuração Externa:** Utiliza um arquivo `.env` para gerenciar chaves de API, evitando que credenciais sejam expostas no código-fonte.

## Próximos Passos e Melhorias

*   Implementar o módulo de ingestão de e-mails (IMAP/POP3 ou Webhooks).
*   Implementar o módulo de envio de respostas automáticas (SMTP).
*   Adicionar um sistema de logging robusto.
*   Criar testes unitários e de integração.
*   Desenvolver uma interface de usuário para monitoramento e revisão manual.
*   Explorar o fine-tuning de modelos de IA para classificações mais precisas e personalizadas.

## Autor

Manus AI
