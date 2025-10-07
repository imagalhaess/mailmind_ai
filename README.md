# MailMind AI - Análise Inteligente de E-mails

**Versão**: 2.1.0  
**Status**: Ativo e em manutenção

🌐 **Aplicação Online**: [https://mailmind-cxpdayn66a-uc.a.run.app/](https://mailmind-cxpdayn66a-uc.a.run.app/)

O MailMind AI é um sistema de análise e curadoria de e-mails que utiliza a IA do Google Gemini para classificar mensagens, resumir conteúdos e sugerir ações, otimizando o fluxo de trabalho de caixas de entrada corporativas.

Esta versão foi completamente refatorada para operar em um ambiente de produção robusto, com foco em **segurança**, **performance** e **escalabilidade**.

## Funcionalidades Principais

| Funcionalidade               | Descrição                                                                                              |
| :--------------------------- | :----------------------------------------------------------------------------------------------------- |
| **Classificação Automática** | Categoriza e-mails em `Produtivo`, `Spam`, `Reclamação`, `Consulta`, `Urgente` e `Outro`.              |
| **Análise com IA**           | Utiliza o Google Gemini para gerar resumos, extrair intenções e sugerir ações específicas.             |
| **Interface Web Intuitiva**  | Permite o upload de arquivos `.txt` e `.pdf` ou a inserção de texto diretamente para análise.          |
| **Análise em Lote**          | Capacidade de processar múltiplos e-mails de uma só vez, separados por `---` ou `From:`.               |
| **Segurança Robusta**        | Implementa `rate limiting`, validação de `API key` e configuração de `CORS` para proteger a aplicação. |
| **Performance Otimizada**    | Utiliza cache com Redis para reduzir a latência e os custos com a API do Gemini.                       |
| **Testes Automatizados**     | Suíte de testes com `pytest` para garantir a estabilidade e a confiabilidade do código.                |
| **Pronto para Produção**     | Otimizado para deploy em contêineres com Docker e orquestração no Google Cloud Run.                    |

## Arquitetura da Solução

A aplicação foi re-arquitetada para seguir as melhores práticas de desenvolvimento em nuvem, garantindo um sistema seguro, escalável e de fácil manutenção.

- **Frontend**: Interface web estática (HTML, CSS, JS) servida diretamente pelo Flask, com design responsivo e focado na usabilidade.
- **Backend**: Aplicação em **Flask** com **Gunicorn** como servidor WSGI, garantindo performance para múltiplas requisições.
- **Cache**: **Redis** é utilizado para cachear os resultados das análises, diminuindo a latência e o consumo da API do Gemini.
- **Segurança**: Múltiplas camadas de segurança, incluindo `Flask-Limiter` para proteção contra abuso e suporte a `API Keys` para endpoints críticos.
- **Containerização**: **Docker** é usado para criar um ambiente de execução consistente e simplificar o deploy.
- **Cloud**: A aplicação está otimizada para deploy no **Google Cloud Run**, com um pipeline de CI/CD configurado via **Google Cloud Build**.

## Pré-requisitos

- Python 3.11 (para execução local)
- Docker (opcional, para execução em container)
- Conta no Google Cloud Platform (para deploy)
- Chave de API do Google Gemini
- `gcloud` CLI instalado e configurado (para deploy)

## Instalação e Execução Local

Para execução local, você pode usar Python diretamente ou Docker.

### Opção 1: Python Direto

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/imagalhaess/mailmind_ai.git
    cd mailmind_ai
    ```

2.  **Configure as variáveis de ambiente:**

    Crie um arquivo `.env` com suas configurações. A variável `GEMINI_API_KEY` é obrigatória.

    ```bash
    # Crie o arquivo .env
    echo "GEMINI_API_KEY=sua_chave_aqui" > .env
    ```

3.  **Instale as dependências e execute:**

    ```bash
    # Crie e ative um ambiente virtual
    python3 -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate

    # Instale as dependências
    pip install -r requirements.txt

    # Execute a aplicação
    python wsgi.py
    ```

4.  **Acesse a aplicação:**

    Acesse [http://localhost:8080](http://localhost:8080) no seu navegador.

    **Nota**: O `wsgi.py` usa porta 8080 por padrão. Para usar a porta 8001 (configuração do config.py), execute: `python -m app`

### Opção 2: Docker

1.  **Clone e configure:**

    ```bash
    git clone https://github.com/imagalhaess/mailmind_ai.git
    cd mailmind_ai
    echo "GEMINI_API_KEY=sua_chave_aqui" > .env
    ```

2.  **Build e execute:**

    ```bash
    docker build -t mailmind .
    docker run -p 8080:8080 --env-file .env mailmind
    ```

## Testes Automatizados

O projeto possui uma suíte de testes automatizados para garantir a qualidade e a estabilidade do código. Para executar os testes:

1.  **Instale as dependências:**

    ```bash
    # Crie e ative um ambiente virtual (recomendado)
    python3 -m venv venv
    source venv/bin/activate

    # Instale as dependências
    pip install -r requirements.txt
    ```

2.  **Execute o Pytest:**

    ```bash
    pytest
    ```

    Para ver o relatório de cobertura de testes, execute:

    ```bash
    pytest --cov=app
    ```

## Deploy no Google Cloud Run

A aplicação está configurada para deploy contínuo (CI/CD) no Google Cloud Run usando o Google Cloud Build e o GitHub Actions.

### Deploy Manual

Para fazer o deploy manualmente, utilize o script `deploy.sh`.

1.  **Autentique-se no gcloud:**

    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

2.  **Execute o script de deploy:**

    O script utiliza o ID do projeto `mailmind-ai-474220` por padrão. Se precisar alterar, passe o ID como argumento.

    ```bash
    ./deploy.sh
    # Ou, para um projeto diferente:
    # ./deploy.sh SEU_OUTRO_PROJECT_ID
    ```

### Deploy Automático (CI/CD)

O deploy é acionado automaticamente via **Google Cloud Build** quando você faz push para o repositório. Para que funcione, é necessário configurar os seguintes **secrets no Google Secret Manager** dentro do seu projeto:

- `GEMINI_API_KEY`: Sua chave da API do Gemini.
- `SMTP_PASSWORD`: A senha do seu servidor SMTP (se for usar o envio de e-mails).

**Configuração do Cloud Build:**

1. Habilite as APIs necessárias no Google Cloud Console
2. Configure o trigger do Cloud Build para o seu repositório
3. O arquivo `cloudbuild.yaml` já está configurado para o deploy automático

## Estrutura do Projeto

```
mailmind_ai/
├── app/                        # Código da aplicação Flask
│   ├── __init__.py
│   ├── app.py                  # Factory da aplicação e rotas
│   ├── config.py               # Configuração centralizada
│   ├── providers/              # Clientes de serviços externos (Gemini)
│   ├── services/               # Lógica de negócio
│   ├── static/                 # Arquivos da interface web (HTML, CSS, JS)
│   └── utils/                  # Funções utilitárias
├── tests/                      # Testes automatizados
├── docs/                       # Documentação técnica
├── Dockerfile                  # Define a imagem de produção
├── cloudbuild.yaml             # Configuração para Google Cloud Build
├── deploy.sh                   # Script para deploy manual
├── requirements.txt            # Dependências Python
├── wsgi.py                     # Entry point para produção
└── README.md                   # Esta documentação
```

## Licença

Este projeto foi desenvolvido por Isabela Mattos como parte de um case de desenvolvimento técnico.
Foram utilizados todos os meios de pesquisa disponíveis.
Agradecimentos especiais à comunidade de código aberto.
