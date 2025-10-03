# 📧 Configuração SendGrid para MailMind

## 🎯 Email Configurado: `mailmindai25@gmail.com`

Este guia explica como configurar o SendGrid para usar o email `mailmindai25@gmail.com` como remetente das respostas automáticas do MailMind.

## 📋 Pré-requisitos

- ✅ Conta SendGrid criada
- ✅ Email `mailmindai25@gmail.com` verificado no SendGrid
- ✅ API Key do SendGrid gerada

## 🔧 Configuração no SendGrid

### 1. **Verificar o Email no SendGrid**

1. Acesse [SendGrid Dashboard](https://app.sendgrid.com/)
2. Vá em **Settings** → **Sender Authentication**
3. Clique em **Single Sender Verification**
4. Adicione o email `mailmindai25@gmail.com`
5. Verifique o email através do link enviado para `mailmindai25@gmail.com`

### 2. **Criar API Key**

1. Vá em **Settings** → **API Keys**
2. Clique em **Create API Key**
3. Nome: `MailMind Production`
4. Permissões: **Full Access** (para desenvolvimento)
5. Copie a API Key gerada

### 3. **Configurar Domínio (Opcional)**

Para melhor deliverability, configure o domínio:

1. Vá em **Settings** → **Sender Authentication**
2. Clique em **Domain Authentication**
3. Adicione o domínio `gmail.com` (se aplicável)

## ⚙️ Configuração no .env

Atualize seu arquivo `.env` com as seguintes configurações:

```bash
# Chave do Google AI Studio (Gemini)
GEMINI_API_KEY=AIza...

# Modelo Gemini (opcional)
GEMINI_MODEL=gemini-2.5-flash

# SendGrid SMTP (GRATUITO até 100 emails/dia)
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
```

## 🧪 Teste da Configuração

### 1. **Teste via Interface Web**

1. Inicie a aplicação:

   ```bash
   python app.py
   ```

2. Acesse http://localhost:8001

3. Na aba "Análise de Email":

   - **Conteúdo**: Cole um email de spam
   - **Email do Remetente**: `seu_email@exemplo.com`
   - Clique em "Analisar Email"

4. **Resultado esperado**:
   - ✅ Email enviado de `mailmindai25@gmail.com`
   - ✅ Recebido no endereço informado

### 2. **Teste via API**

```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email_content": "Promoção imperdível! Compre agora!",
    "sender": "seu_email@exemplo.com"
  }'
```

### 3. **Verificar Email Recebido**

1. Acesse sua caixa de entrada do email informado
2. Verifique também a pasta de spam/lixo eletrônico
3. Você deve ver um email de `mailmindai25@gmail.com`

## 📧 Exemplo de Email Enviado

**De**: `mailmindai25@gmail.com`  
**Para**: `seu_email@exemplo.com`  
**Assunto**: `Resposta automática - Email Analyzer`

**Conteúdo**:

```
Olá,

Recebemos sua mensagem e após análise automatizada, identificamos que ela não requer atenção imediata de nossa equipe. Caso acredite que isso seja um engano, por favor, entre em contato através de um dos nossos canais.

Marcar como spam e mover para a pasta de lixo eletrônico.

Esta é uma resposta automática gerada pelo nosso sistema de análise de emails, por favor, não responda para este endereço.

Atenciosamente,
Equipe de Atendimento Automatizado
MailMind System
```

## 🚨 Solução de Problemas

### Problema: "The from address does not match a verified Sender Identity"

**Causa**: Email não verificado no SendGrid

**Solução**:

1. Verifique se `mailmindai25@gmail.com` está em **Single Sender Verification**
2. Confirme o email através do link enviado
3. Aguarde alguns minutos para propagação

### Problema: "Authentication failed"

**Causa**: API Key incorreta

**Solução**:

1. Verifique se a API Key está correta no `.env`
2. Confirme que tem permissões de envio
3. Teste com uma nova API Key

### Problema: "Email não chega"

**Causa**: Possível bloqueio ou spam

**Solução**:

1. Verifique a pasta de spam
2. Confirme que o domínio está autenticado
3. Teste com outro email de destino

## 📊 Limites do SendGrid Gratuito

- **100 emails/dia** (plano gratuito)
- **40.000 emails/mês** (plano gratuito)
- **Rate limit**: 100 emails/hora

## 🔄 Próximos Passos

Após configurar o SendGrid:

1. **Teste completo**: Use o [Guia de Testes](TESTING_GUIDE.md)
2. **Monitoramento**: Acompanhe estatísticas no SendGrid Dashboard
3. **Produção**: Configure domínio autenticado para melhor deliverability
4. **Backup**: Mantenha configuração Gmail SMTP como fallback

## 📞 Suporte

- **SendGrid Docs**: https://docs.sendgrid.com/
- **Status SendGrid**: https://status.sendgrid.com/
- **Suporte**: https://support.sendgrid.com/

---

**✅ Configuração concluída!** O MailMind agora enviará emails de `mailmindai25@gmail.com` via SendGrid.
