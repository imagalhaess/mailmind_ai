# 🔗 Webhook Email Analyzer - Exemplos de Uso

## 📡 Endpoint do Webhook

**URL:** `POST /webhook/email`  
**Formato:** JSON ou Form Data

## 🧪 Exemplos Práticos

### 1. Teste via cURL

```bash
# Email de spam (improdutivo)
curl -X POST http://localhost:8001/webhook/email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "spammer@fake.com",
    "subject": "GANHE DINHEIRO FÁCIL!!!",
    "email_content": "🔥 OFERTA IMPERDÍVEL 🔥\n\nVocê foi selecionado para receber R$ 50.000,00!!!\nClique aqui agora: www.fakesite.com"
  }'

# Email de proposta (produtivo)
curl -X POST http://localhost:8001/webhook/email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "parceiro@startup.com",
    "subject": "Proposta de parceria estratégica",
    "email_content": "Prezados,\n\nSomos uma startup de tecnologia e gostaríamos de propor uma parceria estratégica com sua empresa.\n\nPodemos agendar uma reunião?\n\nAtenciosamente,\nMaria Santos"
  }'
```

### 2. Teste via JavaScript (Node.js)

```javascript
const fetch = require("node-fetch");

async function testWebhook() {
  const response = await fetch("http://localhost:8001/webhook/email", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sender: "cliente@empresa.com",
      subject: "Solicitação de desconto",
      email_content:
        "Olá,\n\nGostaria de solicitar um desconto especial no produto que vocês vendem.\n\nAtenciosamente,\nJoão Silva",
    }),
  });

  const result = await response.json();
  console.log("Resultado:", result);
}

testWebhook();
```

### 3. Teste via Python

```python
import requests
import json

def test_webhook():
    url = 'http://localhost:8001/webhook/email'

    data = {
        'sender': 'cliente@empresa.com',
        'subject': 'Solicitação de desconto',
        'email_content': 'Olá,\n\nGostaria de solicitar um desconto especial no produto que vocês vendem.\n\nAtenciosamente,\nJoão Silva'
    }

    response = requests.post(url, json=data)
    result = response.json()

    print('Status:', response.status_code)
    print('Resultado:', json.dumps(result, indent=2, ensure_ascii=False))

test_webhook()
```

### 4. Teste via PHP

```php
<?php
$url = 'http://localhost:8001/webhook/email';

$data = [
    'sender' => 'cliente@empresa.com',
    'subject' => 'Solicitação de desconto',
    'email_content' => "Olá,\n\nGostaria de solicitar um desconto especial no produto que vocês vendem.\n\nAtenciosamente,\nJoão Silva"
];

$options = [
    'http' => [
        'header' => "Content-type: application/json\r\n",
        'method' => 'POST',
        'content' => json_encode($data)
    ]
];

$context = stream_context_create($options);
$result = file_get_contents($url, false, $context);

echo "Resultado: " . $result;
?>
```

## 🔄 Integração com Serviços de Email

### Gmail API + Webhook

```javascript
// Exemplo de integração com Gmail API
const { google } = require("googleapis");

async function processGmailEmails() {
  const gmail = google.gmail({ version: "v1", auth: oauth2Client });

  // Busca emails não lidos
  const response = await gmail.users.messages.list({
    userId: "me",
    q: "is:unread",
  });

  for (const message of response.data.messages || []) {
    const email = await gmail.users.messages.get({
      userId: "me",
      id: message.id,
    });

    // Envia para o webhook
    await fetch("http://localhost:8001/webhook/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sender: email.data.payload.headers.find((h) => h.name === "From").value,
        subject: email.data.payload.headers.find((h) => h.name === "Subject")
          .value,
        email_content: email.data.snippet,
      }),
    });
  }
}
```

### Outlook API + Webhook

```javascript
// Exemplo de integração com Outlook API
async function processOutlookEmails() {
  const response = await fetch("https://graph.microsoft.com/v1.0/me/messages", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
  });

  const emails = await response.json();

  for (const email of emails.value) {
    // Envia para o webhook
    await fetch("http://localhost:8001/webhook/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sender: email.from.emailAddress.address,
        subject: email.subject,
        email_content: email.bodyPreview,
      }),
    });
  }
}
```

## 📊 Resposta do Webhook

### Sucesso (Email Individual)

```json
{
  "status": "success",
  "message": "Email processado automaticamente via webhook",
  "result": {
    "categoria": "Spam",
    "atencao_humana": "NÃO",
    "resumo": "Email de spam com oferta irrealista",
    "sugestao": "Responder automaticamente informando que não há interesse",
    "action_result": "✅ Resposta automática ENVIADA para spammer@fake.com",
    "sender": "spammer@fake.com"
  }
}
```

### Sucesso (Múltiplos Emails)

```json
{
  "status": "success",
  "message": "Processados 3 emails automaticamente",
  "results": [
    {
      "email_number": 1,
      "sender": "spammer@fake.com",
      "categoria": "Spam",
      "atencao_humana": "NÃO",
      "action_result": "✅ Resposta automática ENVIADA para spammer@fake.com"
    },
    {
      "email_number": 2,
      "sender": "parceiro@startup.com",
      "categoria": "Proposta de Parceria",
      "atencao_humana": "SIM",
      "action_result": "✅ ENVIADO para CUADORIA HUMANA"
    }
  ]
}
```

### Erro

```json
{
  "error": "Email content is required"
}
```

## 🚀 Casos de Uso Reais

1. **Integração com CRM**: Automatizar análise de emails recebidos
2. **Filtro de Spam**: Processar emails automaticamente
3. **Roteamento Inteligente**: Direcionar emails para equipes corretas
4. **Análise de Sentimento**: Classificar emails por urgência
5. **Resposta Automática**: Responder spam automaticamente

## 🔧 Configuração de Produção

Para usar em produção, configure:

1. **HTTPS**: Use certificado SSL
2. **Autenticação**: Adicione token de autenticação
3. **Rate Limiting**: Limite requisições por minuto
4. **Logs**: Configure logging detalhado
5. **Monitoramento**: Use ferramentas como Prometheus/Grafana
