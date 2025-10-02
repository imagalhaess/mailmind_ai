# Setup SendGrid (Gratuito) - 3 minutos

## Passo a passo rápido:

1. **Crie conta gratuita:**

   - Acesse: https://sendgrid.com/
   - Clique "Start for free"
   - Preencha dados básicos

2. **Crie API Key:**

   - Faça login no dashboard
   - Vá em: Settings → API Keys
   - Clique "Create API Key"
   - Nome: "Email Analyzer Case"
   - Permissions: "Full Access"
   - Copie a chave gerada

3. **Configure .env:**

   ```bash
   cp .env.example .env
   ```

   Edite `.env` com sua chave:

   ```
   SMTP_PASSWORD=sua_chave_sendgrid_aqui
   NOREPLY_ADDRESS=seuemail@gmail.com
   ```

4. **Teste:**
   ```bash
   python app.py
   ```

## Limites gratuitos:

- ✅ 100 emails/dia
- ✅ Sem expiração
- ✅ Perfeito para o case

## Alternativa (se SendGrid der problema):

Use Gmail com senha de app:

- SMTP_HOST=smtp.gmail.com
- SMTP_USER=seuemail@gmail.com
- SMTP_PASSWORD=senha_de_app_do_gmail
