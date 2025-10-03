# 📋 Regras de Negócio - Email Analyzer

## 🎯 Objetivo Principal

O Email Analyzer tem como objetivo **automatizar a análise e curadoria de emails**, classificando-os como produtivos ou improdutivos e executando ações automáticas baseadas nessa classificação.

## 🧠 Lógica de Classificação

### Critérios de Análise (via Gemini AI)

O sistema utiliza o **Google Gemini 2.5 Flash** para analisar emails com base nos seguintes critérios:

#### 📧 **Emails IMPRODUTIVOS** (Não requerem atenção humana)

- **Spam**: Ofertas fraudulentas, phishing, golpes
- **Marketing não solicitado**: Promoções não autorizadas
- **Conteúdo irrelevante**: Emails sem relação com o negócio
- **Solicitações genéricas**: Pedidos de desconto sem contexto
- **Conteúdo duplicado**: Emails repetitivos ou automáticos

**Exemplos**:

```
🔥 OFERTA IMPERDÍVEL 🔥
Você foi selecionado para receber R$ 50.000,00!!!
Clique aqui agora: www.fakesite.com
```

#### 📈 **Emails PRODUTIVOS** (Requerem atenção humana)

- **Propostas de parceria**: Oportunidades de negócio
- **Solicitações específicas**: Pedidos com contexto claro
- **Clientes potenciais**: Interessados em produtos/serviços
- **Feedback**: Sugestões ou reclamações construtivas
- **Oportunidades comerciais**: Negócios reais

**Exemplos**:

```
Prezados,

Somos uma startup de tecnologia e gostaríamos de propor
uma parceria estratégica com sua empresa.

Podemos agendar uma reunião?

Atenciosamente,
Maria Santos
```

## ⚡ Ações Automáticas

### 🔴 **Para Emails IMPRODUTIVOS**

**Ação**: Resposta automática para o **remetente original**

**Conteúdo da Resposta**:

```
Olá,

Recebemos sua mensagem e após análise automatizada,
identificamos que ela não requer atenção imediata de nossa equipe. Caso acredite que isso seja um engano, por favor, entre em contato através de um dos nossos canais.

[Sugestão específica baseada na análise]

Esta é uma resposta automática gerada pelo nosso sistema
de análise de emails, por favor, não responda para este endereço.

Atenciosamente,
Equipe de Atendimento Automatizado
MailMind System
```

**Objetivos**:

- Reduzir spam
- Informar sobre política de email
- Manter profissionalismo
- Liberar tempo da equipe

### 🟢 **Para Emails PRODUTIVOS**

**Ação**: Encaminhamento para **curadoria humana**

**Destinatário**: `autoucase@tuamaeaquelaursa.com` (configurável)

**Conteúdo do Encaminhamento**:

```
Email recebido para curadoria humana:

REMETENTE: [email_do_remetente]
CATEGORIA: [categoria_detectada]
RESUMO: [resumo_gerado_pela_ia]

SUGESTÃO/AÇÃO: [sugestão_da_ia]

--- CONTEÚDO ORIGINAL ---
[primeiros_500_caracteres_do_email]...

Este email foi automaticamente encaminhado pelo sistema MailMind.
```

**Objetivos**:

- Garantir que oportunidades não sejam perdidas
- Permitir análise humana detalhada
- Manter qualidade do atendimento
- Priorizar leads qualificados

## 🔄 Fluxo de Processamento

### 1. **Recebimento do Email**

- Via interface web (`POST /analyze`)
- Via webhook (`POST /webhook/email`)
- Via upload de arquivo (análise em lote)

### 2. **Pré-processamento**

- Limpeza de texto
- Tokenização básica
- Remoção de caracteres especiais

### 3. **Análise via IA**

- Envio para Google Gemini
- Prompt estruturado para classificação
- Resposta em formato JSON

### 4. **Classificação e Ação**

- Parse da resposta JSON
- Determinação da ação (resposta/encaminhamento)
- Execução da ação automática

### 5. **Registro e Feedback**

- Log da operação
- Retorno do resultado
- Possível notificação

## 📊 Critérios de Qualidade

### ✅ **Classificação Correta**

- **Precisão**: Minimizar falsos positivos/negativos
- **Consistência**: Mesmo email = mesma classificação
- **Contexto**: Considerar contexto do negócio

### ⚡ **Performance**

- **Tempo de resposta**: < 5 segundos por email
- **Disponibilidade**: 99% uptime
- **Throughput**: Suportar análise em lote

### 🔒 **Segurança**

- **Dados sensíveis**: Não armazenar conteúdo de emails
- **Autenticação**: Validar origem dos webhooks
- **Rate limiting**: Prevenir abuso

## 🎛️ Configurações de Negócio

### **Endereços de Email**

- `NOREPLY_ADDRESS`: Email para respostas automáticas
- `CURATOR_ADDRESS`: Email para curadoria humana
- `SMTP_CONFIG`: Configurações de envio

### **Limites e Thresholds**

- **Tamanho máximo**: 10MB por arquivo
- **Emails por lote**: Máximo 100 emails
- **Timeout**: 30 segundos por análise

### **Personalização**

- **Prompt do Gemini**: Customizável por cliente
- **Templates de resposta**: Adaptáveis
- **Regras de negócio**: Configuráveis

## 🚨 Tratamento de Exceções

### **Falhas de IA**

- **Timeout**: Retry com timeout maior
- **Rate limit**: Queue para processamento posterior
- **Erro de parsing**: Fallback para classificação manual

### **Falhas de Email**

- **SMTP indisponível**: Modo simulação
- **Email inválido**: Validação e erro claro
- **Quota excedida**: Notificação e pause

### **Falhas de Sistema**

- **Memória**: Processamento em chunks menores
- **Disco**: Limpeza automática de logs
- **Rede**: Retry automático

## 📈 Métricas de Negócio

### **Eficiência**

- **Emails processados/hora**
- **Taxa de automação** (emails que não precisaram de intervenção humana)
- **Tempo médio de resposta**

### **Qualidade**

- **Taxa de classificação correta**
- **Feedback dos curadores**
- **Redução de spam**

### **Custo**

- **Custo por email processado**
- **Economia de tempo da equipe**
- **ROI da automação**

## 🔮 Evolução das Regras

### **Aprendizado Contínuo**

- **Feedback loop**: Curadores podem marcar classificações incorretas
- **Ajuste de prompts**: Melhoria baseada em resultados
- **Novos critérios**: Adaptação a mudanças no negócio

### **Expansão de Funcionalidades**

- **Análise de sentimento**: Detectar urgência/prioridade
- **Categorização avançada**: Sub-categorias específicas
- **Integração CRM**: Sincronização com sistemas existentes

## 🎯 Casos de Uso Específicos

### **E-commerce**

- **Produtivos**: Pedidos, dúvidas sobre produtos, reclamações
- **Improdutivos**: Spam promocional, ofertas genéricas

### **SaaS**

- **Produtivos**: Suporte técnico, solicitações de features, feedback
- **Improdutivos**: Marketing não solicitado, spam

### **Consultoria**

- **Produtivos**: Propostas de projeto, solicitações de orçamento
- **Improdutivos**: Spam, ofertas irrelevantes

## ⚖️ Considerações Éticas

### **Privacidade**

- **Não armazenar**: Conteúdo de emails pessoais
- **Anonimização**: Remover dados sensíveis dos logs
- **Consentimento**: Respeitar preferências de comunicação

### **Transparência**

- **Disclosure**: Informar sobre análise automática
- **Opt-out**: Permitir desistência
- **Auditoria**: Logs de todas as ações

---

**Última atualização**: 02/10/2025  
**Versão**: 1.0.0  
**Status**: Implementado e em produção
