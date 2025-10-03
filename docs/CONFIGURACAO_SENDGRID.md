# ⚙️ Configuração .env para SendGrid

## 📧 Email: `mailmindai25@gmail.com`

Copie e cole esta configuração no seu arquivo `.env`:

```bash
# Configuração SendGrid para MailMind
# Email configurado: mailmindai25@gmail.com

# Chave do Google AI Studio (Gemini)
GEMINI_API_KEY=AIza...

# Modelo Gemini (opcional)
GEMINI_MODEL=gemini-2.5-flash

# SendGrid SMTP (GRATUITO até 100 emails/dia)
# 1. Crie conta em: https://sendgrid.com/
# 2. Vá em Settings > API Keys > Create API Key
# 3. Use a chave como SMTP_PASSWORD
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.sua_chave_sendgrid_aqui

# Email que aparece como remetente (configurado no SendGrid)
NOREPLY_ADDRESS=mailmindai25@gmail.com

# Email para onde encaminhar casos que precisam de curadoria humana
CURATOR_ADDRESS=autoucase@tuamaeaquelaursa.com

# Configurações da aplicação
APP_SECRET=dev-secret-key
PORT=8001

# Gmail SMTP (fallback - opcional)
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_SMTP_USER=mailmindai25@gmail.com
GMAIL_SMTP_PASSWORD=sua_senha_app_gmail
```

## 🔑 O que você precisa fazer:

1. **Substitua `AIza...`** pela sua chave real do Google Gemini
2. **Substitua `SG.sua_chave_sendgrid_aqui`** pela sua API Key do SendGrid
3. **Substitua `sua_senha_app_gmail`** pela senha de app do Gmail (opcional, como fallback)

## 📋 Passos no SendGrid:

1. Acesse https://sendgrid.com/
2. Crie uma conta gratuita
3. Vá em **Settings** → **API Keys** → **Create API Key**
4. Nome: `MailMind Production`
5. Permissões: **Full Access**
6. Copie a API Key (começa com `SG.`)
7. Vá em **Settings** → **Sender Authentication** → **Single Sender Verification**
8. Adicione `mailmindai25@gmail.com`
9. Verifique o email através do link enviado

## ✅ Teste:

Após configurar, teste com:

```bash
python app.py
```

Acesse http://localhost:8001 e teste com qualquer email real seu
