#  Arquitetura do MailMind

##  Visão Geral

O **MailMind** é um sistema inteligente de análise e curadoria de emails que utiliza IA (Google Gemini) para classificar emails como produtivos ou improdutivos e executar ações automáticas baseadas na classificação.

##  Objetivos do Sistema

1. **Automatizar** a análise de emails recebidos
2. **Classificar** emails como produtivos (requerem atenção humana) ou improdutivos (spam/lixo)
3. **Executar ações automáticas**:
   - **Improdutivos**: Resposta automática para o remetente original
   - **Produtivos**: Encaminhamento para curadoria humana
4. **Processar em lote** múltiplos emails de um arquivo
5. **Fornecer webhook** para integração com sistemas externos

##  Arquitetura Geral

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   Gemini AI    │
│   (Templates)   │◄──►│   (app.py)      │◄──►│   (API)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Email Sender   │
                       │   (Fallback)     │
                       └─────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌─────────────┐         ┌─────────────┐
            │   SendGrid   │         │ Gmail SMTP  │
            │   (Primary)  │         │ (Fallback)  │
            └─────────────┘         └─────────────┘
```

##  Sistema de Fallback de Email

O sistema implementa uma estratégia robusta de fallback para garantir que emails sempre sejam enviados:

### **Estratégia de Fallback**:

1. **SendGrid SMTP** (Primário)
   - Provedor profissional
   - Boa reputação de entrega
   - Limite gratuito de 100 emails/dia
2. **Gmail SMTP** (Fallback)
   - Configuração simples
   - Boa compatibilidade
   - Confiável como backup
3. **Modo Simulação** (Último recurso)
   - Logs detalhados
   - Sistema continua funcionando
   - Fácil debugging

### **Fluxo de Decisão**:

```
Tentar SendGrid → Sucesso? → Usar SendGrid
     ↓ Falha
Tentar Gmail → Sucesso? → Usar Gmail
     ↓ Falha
Modo Simulação → Log + Continuar
```

##  Estrutura de Diretórios

```
mailmind_ai/
├── app.py                    # Aplicação Flask principal
├── main.py                   # Exemplo CLI (demonstração)
├── requirements.txt          # Dependências Python
├── .env.example             # Template de variáveis de ambiente
├── README.md                 # Documentação principal
├── docs/                     # Documentação completa
│   ├── ARCHITECTURE.md       # Este arquivo
│   ├── TECHNICAL_DECISIONS.md # Decisões técnicas
│   ├── DEVELOPMENT_GUIDE.md  # Guia de desenvolvimento
│   └── LGPD_COMPLIANCE.md    # Conformidade LGPD
├── app/                      # Código da aplicação
│   ├── __init__.py           # Pacote principal
│   ├── app.py                # Aplicação Flask
│   ├── config.py             # Configurações centralizadas
│   ├── providers/            # Provedores externos
│   │   └── gemini_client.py  # Cliente Google Gemini
│   ├── services/             # Lógica de negócio
│   │   └── email_analyzer.py # Serviço de análise de emails
│   ├── utils/                # Utilitários
│   │   ├── text_preprocess.py # Pré-processamento de texto
│   │   └── email_sender.py   # Envio de emails
│   ├── static/               # Interface web
│   │   ├── index.html        # Página principal
│   │   ├── css/style.css     # Estilos
│   │   └── js/app.js         # JavaScript
│   └── tests/                # Testes unitários
│       └── TESTING_GUIDE.md  # Guia de testes
└── render.yaml               # Configuração de deploy
```

##  Componentes Principais

### 1. **Flask App (app.py)**

- **Responsabilidade**: Orquestração geral, rotas HTTP, interface web
- **Padrão**: MVC (Model-View-Controller)
- **Rotas**:
  - `GET /` - Interface principal
  - `POST /analyze` - Análise de emails
  - `POST /webhook/email` - Webhook para recebimento automático
  - `GET /webhook/test` - Interface de teste do webhook
  - `GET /test/<tipo>` - Testes com dados mock

### 2. **Configuração (config.py)**

- **Responsabilidade**: Centralizar todas as configurações
- **Padrão**: Singleton de configuração
- **Variáveis**:
  - `GEMINI_API_KEY` - Chave da API do Google Gemini
  - `SMTP_*` - Configurações de email
  - `CURATOR_ADDRESS` - Email para curadoria humana
  - `NOREPLY_ADDRESS` - Email de resposta automática

### 3. **Serviço de Análise (services/email_analyzer.py)**

- **Responsabilidade**: Lógica de negócio para análise de emails
- **Padrão**: Service Layer
- **Métodos**:
  - `analyze(email_content)` - Analisa um email usando Gemini

### 4. **Cliente Gemini (providers/gemini_client.py)**

- **Responsabilidade**: Comunicação com API do Google Gemini
- **Padrão**: Provider Pattern
- **Métodos**:
  - `generate_content(prompt)` - Gera análise via Gemini

### 5. **Utilitários**

- **text_preprocess.py**: Pré-processamento de texto (tokenização, limpeza)
- **email_sender.py**: Envio de emails via SMTP

##  Fluxo de Dados

### Análise Individual

```
1. Usuário envia email via interface web
2. Flask recebe POST /analyze
3. Email é pré-processado (text_preprocess)
4. Serviço de análise chama Gemini
5. Gemini retorna classificação JSON
6. Sistema executa ação baseada na classificação:
   - Improdutivo → Resposta automática
   - Produtivo → Encaminhamento para curadoria
7. Resultado é exibido na interface
```

### Análise em Lote

```
1. Usuário envia arquivo com múltiplos emails
2. Sistema detecta múltiplos emails (split_multiple_emails)
3. Para cada email:
   - Pré-processa
   - Analisa via Gemini
   - Executa ação automática
4. Resultados são consolidados e exibidos
```

### Webhook

```
1. Sistema externo envia POST /webhook/email
2. Flask recebe dados JSON/Form
3. Processa como análise individual ou em lote
4. Retorna resultado JSON
```

##  Padrões de Design Utilizados

### 1. **Separation of Concerns**

- **Configuração**: `config.py`
- **Lógica de negócio**: `services/`
- **Provedores externos**: `providers/`
- **Utilitários**: `utils/`
- **Interface**: `templates/`

### 2. **Dependency Injection**

- Configurações são injetadas nos serviços
- Cliente Gemini é injetado no serviço de análise

### 3. **Provider Pattern**

- `GeminiClient` abstrai a comunicação com a API
- Facilita troca de provedor de IA no futuro

### 4. **Service Layer**

- `EmailAnalyzerService` encapsula regras de negócio
- Separa lógica de negócio da interface

##  Segurança

### 1. **Variáveis de Ambiente**

- Chaves de API não ficam no código
- Template `.env.example` para configuração

### 2. **Validação de Entrada**

- Validação de dados recebidos via webhook
- Sanitização de conteúdo de email

### 3. **Tratamento de Erros**

- Try/catch em operações críticas
- Logs detalhados para debugging
- Fallbacks para falhas de API

##  Monitoramento e Logs

### 1. **Logging Estruturado**

- Logs de INFO para operações normais
- Logs de ERROR para falhas
- Logs de DEBUG para desenvolvimento

### 2. **Métricas Importantes**

- Emails processados por minuto
- Taxa de sucesso da API Gemini
- Tempo de resposta das análises

##  Escalabilidade

### 1. **Processamento Assíncrono** (Futuro)

- Implementar filas (Redis/Celery)
- Processar emails em background

### 2. **Cache** (Futuro)

- Cache de análises similares
- Cache de configurações

### 3. **Load Balancing** (Futuro)

- Múltiplas instâncias da aplicação
- Distribuição de carga

##  Melhorias Futuras

### 1. **Webhook Avançado** (WIP)

- Autenticação via token
- Rate limiting
- Webhook retry logic
- Webhook signature validation

### 2. **Integração com Email Providers**

- Gmail API integration
- Outlook API integration
- IMAP/POP3 support

### 3. **Machine Learning**

- Treinamento de modelo próprio
- Fine-tuning baseado em feedback
- Análise de sentimento avançada

### 4. **Dashboard Analytics**

- Métricas de performance
- Relatórios de classificação
- Visualização de tendências

##  Testes

### 1. **Testes Unitários**

- `tests/test_email_analyzer.py`
- Mock do cliente Gemini
- Testes de parsing JSON

### 2. **Testes de Integração** (Futuro)

- Testes end-to-end
- Testes de webhook
- Testes de envio de email

##  Convenções de Código

### 1. **Python**

- PEP 8 compliance
- Type hints onde possível
- Docstrings em funções públicas

### 2. **Nomenclatura**

- Classes: PascalCase (`EmailAnalyzerService`)
- Funções: snake_case (`analyze_email`)
- Constantes: UPPER_CASE (`GEMINI_API_KEY`)

### 3. **Estrutura de Arquivos**

- Um arquivo por classe/funcionalidade
- Imports organizados (stdlib, third-party, local)
- Separação clara de responsabilidades

##  Configuração de Desenvolvimento

### 1. **Ambiente Virtual**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. **Variáveis de Ambiente**

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. **Execução**

```bash
python app.py
```

##  Dependências Principais

- **Flask**: Framework web
- **google-generativeai**: Cliente Google Gemini
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **pdfminer.six**: Processamento de PDFs
- **pytest**: Framework de testes

---

**Última atualização**: 03/01/2025  
**Versão**: 1.0.0  
**Status**: Produção (com melhorias futuras planejadas)
