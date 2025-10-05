# MailMind - Sistema de Análise Inteligente de Emails

Sistema de análise e curadoria de e-mails usando IA (Google Gemini) para classificar mensagens e automatizar respostas. Otimize seu tempo usando a IA da forma correta.

## Funcionalidades

- **Classificação Automática**: Categoriza e-mails como Produtivo ou Improdutivo
- **Análise com IA**: Usa Google Gemini para resumir e sugerir ações
- **Respostas Automáticas**: Envia respostas para e-mails improdutivos
- **Encaminhamento**: Direciona casos complexos para curadoria humana
- **Interface Web**: Upload de arquivos (.txt/.pdf) ou entrada de texto

## Pré-requisitos

- Python 3.10+
- Chave de API do Google Gemini
- Conta SendGrid (opcional, para envio de e-mails/respostas automáticas)

## Instalação

1. **Clone e configure o ambiente:**

   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
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

## Configuração

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
python -m app.app
# Acesse: http://localhost:8001
```

### CLI (exemplos):

```bash
python main.py
```

## Estrutura do Projeto

```
mailmind/
├── app.py                    #  Ponto de entrada principal
├── main.py                   #  Exemplo CLI (demonstração)
├── requirements.txt          #  Dependências Python
├── .env.example              #  Template de variáveis de ambiente
├── app/                      #  Código da aplicação
│   ├── __init__.py           #  Pacote principal
│   ├── app.py                #  Aplicação Flask
│   ├── config.py             #  Configurações
│   ├── providers/            #  Provedores externos
│   │   └── gemini_client.py  #  Cliente Google Gemini
│   ├── services/             #  Lógica de negócio
│   │   └── email_analyzer.py #  Serviço de análise
│   ├── utils/                #  Utilitários
│   │   ├── text_preprocess.py #  Pré-processamento NLP
│   │   └── email_sender.py   #  Envio de emails
│   └── static/               #  Interface web moderna
│       ├── index.html        #  Página principal
│       ├── css/style.css     #  Estilos modernos
│       └── js/app.js         #  JavaScript interativo
└── docs/                     #  Documentação completa
    ├── ARCHITECTURE.md       #  Arquitetura do sistema
    ├── TECHNICAL_DECISIONS.md #  Decisões técnicas
    ├── DEVELOPMENT_GUIDE.md  #  Guia de desenvolvimento
    └── LGPD_COMPLIANCE.md    #  Conformidade LGPD
```

## Testes

### Teste Rápido

```bash
# Iniciar aplicação
python app.py

# Acessar interface
# http://localhost:8001
```

### Guia Completo de Testes

Consulte **[Guia de Testes](app/tests/TESTING_GUIDE.md)** para instruções detalhadas sobre:

- ✅ Como testar todas as funcionalidades
- ✅ Use qualquer email real para receber as mensagens
- ✅ Cenários de teste passo a passo
- ✅ Verificação de problemas comuns
- ✅ **Sistema de fallback**: SendGrid → Gmail SMTP → Simulação

## Arquitetura

O sistema segue princípios de Clean Code:

- **Separação de Responsabilidades**: Cada módulo tem uma função específica
- **Injeção de Dependências**: Configurações externas via `.env`
- **Tratamento de Erros**: Validação robusta e logging
- **Testabilidade**: Estrutura preparada para testes unitários

## Deploy

Para produção, use um servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

## Próximos Passos

### ✅ **Implementado**

- [x] Sistema de análise automática de emails
- [x] Classificação produtivo/improdutivo via Gemini AI
- [x] Respostas automáticas para spam
- [x] Encaminhamento para curadoria humana
- [x] Análise em lote de múltiplos emails
- [x] Interface web completa
- [x] Sistema de envio de emails via SMTP/Gmail
- [x] Webhook básico para integração

### **Em Progresso (WIP)**

- [ ] **Webhook Avançado**: Autenticação, rate limiting, retry logic
- [ ] **Integração com Email Providers**: Gmail API, Outlook API
- [ ] **Dashboard Analytics**: Métricas e relatórios
- [ ] **Machine Learning**: Modelo próprio, fine-tuning

### **Planejado**

- [ ] Autenticação de usuários
- [ ] Cache para melhorar performance
- [ ] Testes automatizados mais abrangentes
- [ ] Logging estruturado avançado
- [ ] Monitoramento de saúde da aplicação
- [ ] Processamento assíncrono (Redis/Celery)
- [ ] Análise de sentimento avançada

## Documentação Completa

- **[Guia de Testes](app/tests/TESTING_GUIDE.md)** - 🧪 Como testar todas as funcionalidades
- **[Arquitetura](docs/ARCHITECTURE.md)** - 🏛️ Decisões arquiteturais e estrutura do sistema
- **[Decisões Técnicas](docs/TECHNICAL_DECISIONS.md)** - 🔧 Por que cada tecnologia foi escolhida
- **[Guia de Desenvolvimento](docs/DEVELOPMENT_GUIDE.md)** - 👨‍💻 Como contribuir e desenvolver
- **[Conformidade LGPD](docs/LGPD_COMPLIANCE.md)** - 🛡️ Política de privacidade e proteção de dados

## 📝 Licença

Este projeto foi desenvolvido por Isabela Mattos para o processo seletivo da AutoU.
