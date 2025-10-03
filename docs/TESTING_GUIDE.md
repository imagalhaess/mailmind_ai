# 🧪 Guia de Testes - MailMind

Este guia explica como testar todas as funcionalidades do MailMind de forma prática e eficiente.

## 📋 Pré-requisitos para Testes

### 1. Configuração Básica

- ✅ Python 3.10+ instalado
- ✅ Ambiente virtual ativado (`.venv`)
- ✅ Dependências instaladas (`pip install -r requirements.txt`)
- ✅ Chave da API do Google Gemini configurada no `.env`

### 2. Configuração de Email (Opcional)

Para testar o envio de emails automáticos, configure no `.env`:

```bash
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_SMTP_USER=seu_email@gmail.com
GMAIL_SMTP_PASSWORD=sua_senha_app_gmail
NOREPLY_ADDRESS=noreply@seudominio.com
CURATOR_ADDRESS=autoucase@tuamaeaquelaursa.com
```

## 🚀 Como Executar a Aplicação

### 1. Iniciar o Servidor

```bash
# Ativar ambiente virtual
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Iniciar aplicação
python app.py
```

### 2. Acessar a Interface

- **URL**: http://localhost:8001
- **Status**: Verificar se aparece "MailMind está funcionando corretamente"

## 🧪 Cenários de Teste

### Teste 1: Email Improdutivo (Spam) - Resposta Automática

**Objetivo**: Verificar se emails de spam recebem resposta automática.

**Passos**:

1. Acesse http://localhost:8001
2. Na aba "Análise de Email":

   - **Tipo de entrada**: Selecione "Texto direto"
   - **Conteúdo do email**: Cole o texto abaixo:

     ```
     URGENTE!!! GANHE DINHEIRO FÁCIL!!!

     🔥🔥🔥 OFERTA IMPERDÍVEL 🔥🔥🔥

     Você foi selecionado para receber R$ 50.000,00!!!
     Clique aqui agora: www.fakesite.com/ganhe-dinheiro

     ⚠️ ATENÇÃO: Esta oferta expira em 24 horas!!!
     ⚠️ Não perca esta oportunidade única!!!
     ```

   - **Email do Remetente**: `seu_email@exemplo.com`

3. Clique em "Analisar Email"

**Resultado Esperado**:

- ✅ Categoria: "Spam" ou "Improdutivo"
- ✅ Atenção Humana: "NÃO"
- ✅ Ação: "Resposta automática ENVIADA para o REMETENTE"
- ✅ Email recebido no endereço informado

**Como verificar o email recebido**:

1. Acesse sua caixa de entrada do email informado
2. Verifique também a pasta de spam/lixo eletrônico
3. Você deve ver um email de `mailmindai25@gmail.com` com assunto "Resposta automática - Email Analyzer"

### Teste 2: Email Produtivo - Encaminhamento para Curadoria

**Objetivo**: Verificar se emails importantes são encaminhados para análise humana.

**Passos**:

1. Na aba "Análise de Email":

   - **Tipo de entrada**: Selecione "Texto direto"
   - **Conteúdo do email**: Cole o texto abaixo:

     ```
     Prezados,

     Somos uma startup de tecnologia e gostaríamos de propor uma parceria estratégica
     com sua empresa. Temos uma solução inovadora que pode agregar valor ao seu negócio.

     Podemos agendar uma reunião para apresentar nossa proposta?

     Atenciosamente,
     Maria Santos
     CEO - TechStartup
     ```

   - **Email do Remetente**: `seu_email@exemplo.com`

2. Clique em "Analisar Email"

**Resultado Esperado**:

- ✅ Categoria: "Parceria" ou "Produtivo"
- ✅ Atenção Humana: "SIM"
- ✅ Ação: "ENVIADO para CURADORIA HUMANA"
- ✅ Email encaminhado para: `autoucase@tuamaeaquelaursa.com`

### Teste 3: Upload de Arquivo

**Objetivo**: Testar análise de emails via upload de arquivo.

**Passos**:

1. Crie um arquivo `test_email.txt` com o conteúdo:

   ```
   From: cliente@empresa.com
   Subject: Solicitação de orçamento

   Olá,

   Gostaria de solicitar um orçamento para desenvolvimento de um sistema web.
   Podem me enviar uma proposta?

   Obrigado,
   João Silva
   ```

2. Na aba "Análise de Email":
   - **Tipo de entrada**: Selecione "Arquivo"
   - **Arquivo**: Faça upload do `test_email.txt`
   - **Email do Remetente**: `seu_email@exemplo.com`
3. Clique em "Analisar Email"

**Resultado Esperado**:

- ✅ Categoria: "Solicitação" ou "Produtivo"
- ✅ Atenção Humana: "SIM"
- ✅ Resumo: Deve identificar solicitação de orçamento

### Teste 4: Testes Automáticos (Mock)

**Objetivo**: Testar funcionalidades sem depender da API do Gemini.

**Passos**:

1. Na aba "Testes":
   - Clique em "Teste Improdutivo" para testar resposta automática
   - Clique em "Teste Produtivo" para testar encaminhamento

**Resultado Esperado**:

- ✅ Ambos os testes devem funcionar instantaneamente
- ✅ Mostrar resultados simulados com ações executadas

### Teste 5: Webhook

**Objetivo**: Testar integração via API.

#### **📋 Estrutura JSON Aceita**

O webhook aceita **APENAS** a estrutura JSON simples abaixo. JSONs mais complexos não são interpretados:

```json
{
  "sender": "email@exemplo.com",
  "subject": "Assunto do Email",
  "content": "Conteúdo do email aqui"
}
```

**Campos obrigatórios**:

- `sender`: Email do remetente (string)
- `subject`: Assunto do email (string)
- `content`: Conteúdo do email (string)

**Campos opcionais**:

- `email_content`: Alternativa ao campo `content` (para compatibilidade)

#### **⚠️ Limitações Importantes**:

- **JSON simples apenas**: Não aceita estruturas aninhadas complexas
- **Campos específicos**: Apenas `sender`, `subject`, `content`/`email_content`
- **Sem arrays**: Não aceita listas de emails
- **Sem objetos aninhados**: Não aceita objetos dentro de objetos
- **Sem metadados extras**: Campos como `timestamp`, `headers`, `attachments` são ignorados

#### **❌ Exemplos de JSONs NÃO Aceitos**:

```json
// ❌ Muito complexo - objetos aninhados
{
  "email": {
    "sender": "test@test.com",
    "subject": "Test",
    "content": "Test content"
  },
  "metadata": {
    "timestamp": "2025-01-01",
    "priority": "high"
  }
}

// ❌ Array de emails
[
  {
    "sender": "test1@test.com",
    "subject": "Test 1",
    "content": "Content 1"
  },
  {
    "sender": "test2@test.com",
    "subject": "Test 2",
    "content": "Content 2"
  }
]

// ❌ Campos extras não reconhecidos
{
  "sender": "test@test.com",
  "subject": "Test",
  "content": "Test content",
  "attachments": ["file1.pdf"],
  "headers": {"X-Priority": "1"}
}
```

#### **✅ Exemplos de JSONs Aceitos**:

```json
// ✅ Estrutura básica
{
  "sender": "webhook@teste.com",
  "subject": "Teste via webhook",
  "content": "Este é um teste de integração via webhook."
}

// ✅ Usando email_content (alternativa)
{
  "sender": "test@exemplo.com",
  "subject": "Teste alternativo",
  "email_content": "Conteúdo usando campo alternativo."
}
```

**Passos**:

1. Na aba "Webhook":
   - **Clique em**: "Usar JSON de Teste" (carrega estrutura válida automaticamente)
   - **Ou cole manualmente**:
     ```json
     {
       "sender": "webhook@teste.com",
       "subject": "Teste via webhook",
       "content": "Este é um teste de integração via webhook."
     }
     ```
2. Clique em "Enviar para Webhook"

**Resultado Esperado**:

- ✅ Status: "Sucesso"
- ✅ Resposta: JSON com análise do email
- ✅ Contagem correta de emails produtivos/improdutivos

## 🔍 Verificação de Problemas

### Problema: "Erro na análise"

**Causa**: API do Gemini não respondeu
**Solução**:

1. Verificar se `GEMINI_API_KEY` está configurada no `.env`
2. Testar com dados mock primeiro
3. Verificar conexão com internet

### Problema: "Email não foi enviado"

**Causa**: Configuração SMTP incorreta
**Solução**:

1. Verificar credenciais Gmail no `.env`
2. Usar senha de app do Gmail (não senha normal)
3. Verificar se 2FA está ativado no Gmail

### Problema: "Interface não carrega"

**Causa**: Servidor não iniciou
**Solução**:

1. Verificar se porta 8001 está livre
2. Executar `python app.py` novamente
3. Verificar logs no terminal

## 📧 Email de Teste

**Use qualquer email real seu** para receber as mensagens automáticas

**Sugestões**:

- ✅ Use seu próprio email para testar
- ✅ Ou crie um email temporário para testes
- ✅ **Verifique a pasta de spam se não receber** - emails automáticos podem ser classificados como spam
- ✅ **Remova da pasta de spam** se necessário para testar o recebimento

### 🔄 Sistema de Fallback

O MailMind usa um sistema robusto de fallback para envio de emails:

1. **SendGrid SMTP** (Primário) - Provedor profissional
2. **Gmail SMTP** (Fallback) - Backup confiável
3. **Modo Simulação** (Último recurso) - Para debugging

**Status atual**: Gmail SMTP está funcionando como fallback, garantindo que emails sempre sejam enviados.

## 📬 Email de Curadoria

**Email configurado**: `autocase_curador@tuamaeaquelaursa.com`

### Como Acessar o Email de Curadoria:

1. **Acesse**: https://tuamaeaquelaursa.com
2. **Clique em**: "exemplo@tuamaeaquelaursa"
3. **Digite o email**: `autocase_curador`

### O que Você Verá:

- **Emails Produtivos**: Propostas comerciais, parcerias, dúvidas técnicas, etc.
- **Assunto**: "Email recebido para curadoria humana"
- **Conteúdo**: Detalhes completos do email original + análise da IA
- **Remetente**: Sistema MailMind

### Testando o Encaminhamento:

1. Envie um email **produtivo** (proposta comercial, parceria, etc.)
2. Verifique se aparece na caixa de entrada do `autocase_curador@tuamaeaquelaursa.com`
3. Confirme que o conteúdo está completo e legível

## 🎯 Checklist de Testes Completos

- [ ] ✅ Aplicação inicia sem erros
- [ ] ✅ Interface web carrega corretamente
- [ ] ✅ Análise de email spam funciona
- [ ] ✅ Resposta automática é enviada
- [ ] ✅ Email é recebido no endereço informado
- [ ] ✅ Análise de email produtivo funciona
- [ ] ✅ Encaminhamento para curadoria funciona
- [ ] ✅ Upload de arquivo funciona
- [ ] ✅ Testes mock funcionam
- [ ] ✅ Webhook funciona
- [ ] ✅ Todos os resultados são exibidos corretamente

## 🚀 Próximos Passos

Após completar todos os testes:

1. **Deploy**: Consulte `docs/DEPLOY_GUIDE.md`
2. **Integração**: Consulte `docs/WEBHOOK_EXAMPLES.md`
3. **Desenvolvimento**: Consulte `docs/DEVELOPMENT_GUIDE.md`

---

**💡 Dica**: Use sempre um email real seu para testes, assim você pode verificar facilmente se os emails foram recebidos!
