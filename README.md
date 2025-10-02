# Email Analyzer - AutoU Case

Sistema de análise e curadoria de e-mails usando IA (Google Gemini) para classificar mensagens e sugerir respostas automáticas.

## 🚀 Funcionalidades

- **Classificação Automática**: Categoriza e-mails como Produtivo ou Improdutivo
- **Análise com IA**: Usa Google Gemini para resumir e sugerir ações
- **Respostas Automáticas**: Envia respostas para e-mails improdutivos
- **Encaminhamento**: Direciona casos complexos para curadoria humana
- **Interface Web**: Upload de arquivos (.txt/.pdf) ou entrada de texto

## 📋 Pré-requisitos

- Python 3.10+
- Chave de API do Google Gemini
- Conta SendGrid (opcional, para envio de e-mails)

## 🛠️ Instalação

1. **Clone e configure o ambiente:**

   ```bash
   git clone <seu-repositorio>
   cd email_analyzer
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate   # Windows
   ```

2. **Instale dependências:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais
   ```

## ⚙️ Configuração

### Obrigatório:

- `GEMINI_API_KEY`: Chave do Google AI Studio

### Opcional (para envio de e-mails):

- `SMTP_HOST`: smtp.sendgrid.net
- `SMTP_USER`: apikey
- `SMTP_PASSWORD`: Sua chave SendGrid
- `NOREPLY_ADDRESS`: Email remetente
- `CURATOR_ADDRESS`: Email para curadoria humana

## 🏃‍♂️ Execução

### Interface Web:

```bash
python app.py
# Acesse: http://localhost:8000
```

### CLI (exemplos):

```bash
python main.py
```

## 📁 Estrutura do Projeto

```
email_analyzer/
├── app.py                 # Aplicação Flask (interface web)
├── main.py               # CLI com exemplos
├── config.py             # Configurações e validação
├── providers/
│   └── gemini_client.py  # Cliente Gemini
├── services/
│   └── email_analyzer.py # Lógica de análise
├── utils/
│   ├── text_preprocess.py # Pré-processamento NLP
│   └── email_sender.py   # Envio de e-mails
├── templates/            # Templates HTML
├── tests/               # Testes unitários
└── requirements.txt     # Dependências
```

## 🧪 Testes

```bash
pip install pytest
pytest tests/
```

## 📚 Documentação Adicional

- [Setup SendGrid](SETUP_SENDGRID.md) - Configuração de envio de e-mails

## 🏗️ Arquitetura

O sistema segue princípios de Clean Code:

- **Separação de Responsabilidades**: Cada módulo tem uma função específica
- **Injeção de Dependências**: Configurações externas via `.env`
- **Tratamento de Erros**: Validação robusta e logging
- **Testabilidade**: Estrutura preparada para testes unitários

## 🚀 Deploy

Para produção, use um servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

## 📝 Licença

Este projeto foi desenvolvido para o processo seletivo da AutoU.
