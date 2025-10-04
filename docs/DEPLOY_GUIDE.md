# 🚀 Guia de Deploy - MailMind

## 📋 Opções de Deploy Disponíveis

### 1. **Railway** (Recomendado) ⭐

- ✅ **Gratuito** para projetos pequenos
- ✅ **Deploy automático** via GitHub
- ✅ **Configuração simples** com arquivos mínimos
- ✅ **Suporte nativo** a Python/Flask
- ✅ **Variáveis de ambiente** fáceis de configurar

### 2. **Heroku** (Alternativa)

- ✅ **Gratuito** com limitações
- ✅ **Muito popular** e bem documentado
- ✅ **Suporte completo** a Python
- ⚠️ **Mais complexo** de configurar

### 3. **Render** (Alternativa)

- ✅ **Gratuito** com limitações
- ✅ **Interface moderna**
- ✅ **Deploy automático**
- ⚠️ **Menos popular** que Railway/Heroku

## 🎯 Deploy Recomendado: Railway

### Pré-requisitos

- ✅ Conta no GitHub
- ✅ Conta no Railway (criar gratuitamente)
- ✅ Projeto commitado no GitHub

### Passos para Deploy

#### 1. **Criar Conta no Railway**

- Acesse: https://railway.app
- Clique em "Login" → "Login with GitHub"
- Autorize o acesso ao GitHub

#### 2. **Conectar Repositório**

- No Railway, clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Escolha o repositório `seu-usuario/seu-repositorio`

#### 3. **Configurar Variáveis de Ambiente**

No Railway, vá em "Variables" e adicione:

```bash
# API Gemini
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash

# Email (Gmail SMTP)
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_SMTP_USER=seu_email@gmail.com
GMAIL_SMTP_PASSWORD=sua_senha_app_aqui

# Configurações
NOREPLY_ADDRESS=seu_email@gmail.com
CURATOR_ADDRESS=curador@suaempresa.com
PORT=8000
```

#### 4. **Deploy Automático**

- Railway detectará automaticamente que é um projeto Python
- Usará o `requirements.txt` para instalar dependências
- Executará `python app.py` automaticamente

#### 5. **Acessar Aplicação**

- Railway fornecerá uma URL como: `https://seu-projeto-production.up.railway.app`
- A aplicação estará disponível 24/7

## 🔧 Arquivos Necessários

### `Procfile` (já existe)

```
web: python app.py
```

### `requirements.txt` (já existe)

```
Flask==3.0.0
google-generativeai==0.3.2
python-dotenv==1.0.0
pdfminer.six==20231228
requests==2.31.0
pytest==7.4.3
gunicorn==21.2.0
```

## 🧪 Testando o Deploy

### 1. **Health Check**

```bash
curl https://seu-projeto-production.up.railway.app/health
```

### 2. **Teste de Análise**

```bash
curl -X POST https://seu-projeto-production.up.railway.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email_content": "From: teste@exemplo.com\nSubject: Teste\n\nEste é um email de teste.",
    "sender": "teste@exemplo.com"
  }'
```

### 3. **Teste de Webhook**

```bash
curl -X POST https://seu-projeto-production.up.railway.app/webhook/email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "webhook@teste.com",
    "subject": "Teste via webhook",
    "content": "Este é um teste de integração via webhook."
  }'
```

## 🔍 Monitoramento

### Logs em Tempo Real

- Railway fornece logs em tempo real
- Acesse: Project → Deployments → View Logs

### Métricas

- CPU, Memória, Rede
- Requests por minuto
- Tempo de resposta

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. **Erro de Variáveis de Ambiente**

```bash
# Verificar se todas as variáveis estão configuradas
GEMINI_API_KEY=✅
GMAIL_SMTP_USER=✅
GMAIL_SMTP_PASSWORD=✅
```

#### 2. **Erro de Porta**

```bash
# Railway usa PORT automático, não 8001
PORT=8000  # ou deixar vazio
```

#### 3. **Erro de Dependências**

```bash
# Verificar requirements.txt
pip install -r requirements.txt
```

#### 4. **Erro de Gmail SMTP**

```bash
# Verificar senha de app do Gmail
# Não usar senha normal, usar "App Password"
```

## 📊 Status do Deploy

- ✅ **Código**: Commitado no GitHub
- ✅ **Dependências**: requirements.txt configurado
- ✅ **Configuração**: Procfile criado
- ✅ **Documentação**: Guia completo
- 🔄 **Deploy**: Pronto para Railway

## 🎯 Próximos Passos

1. **Criar conta no Railway**
2. **Conectar repositório GitHub**
3. **Configurar variáveis de ambiente**
4. **Fazer deploy automático**
5. **Testar aplicação em produção**
6. **Atualizar documentação com URL final**

---

**Última atualização**: 03/10/2025  
**Status**: Pronto para deploy  
**Recomendação**: Railway (mais simples e eficiente)
