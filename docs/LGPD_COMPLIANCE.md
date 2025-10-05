# Conformidade LGPD - MailMind

## Avisos Legais Obrigatórios

### ⚠️ **AVISO IMPORTANTE SOBRE DADOS PESSOAIS**

Este sistema processa dados pessoais contidos em emails e está sujeito à **Lei Geral de Proteção de Dados (LGPD)** do Brasil.

### **Política de Privacidade**

#### **1. Dados Coletados**

- **Conteúdo de emails** enviados para análise
- **Endereços de email** dos remetentes
- **Metadados** de processamento (timestamps, categorização)

#### **2. Finalidade do Tratamento**

- **Análise automatizada** de emails para classificação
- **Geração de respostas automáticas** quando aplicável
- **Encaminhamento** de emails produtivos para curadoria humana
- **Melhoria contínua** do sistema de análise

#### **3. Base Legal**

- **Consentimento** do titular dos dados
- **Execução de contrato** ou procedimentos preliminares
- **Legítimo interesse** para operação do serviço

#### **4. Compartilhamento de Dados**

- **Não compartilhamos** dados pessoais com terceiros
- **Dados são processados** apenas pelo sistema MailMind
- **Emails produtivos** são encaminhados apenas para curadoria autorizada

#### **5. Retenção de Dados**

- **Dados são processados** em tempo real
- **Não armazenamos** conteúdo de emails permanentemente
- **Logs técnicos** são mantidos por período mínimo necessário

### **Direitos dos Titulares**

Conforme a LGPD, você tem direito a:

- ✅ **Acesso**: Solicitar informações sobre seus dados
- ✅ **Correção**: Corrigir dados incorretos
- ✅ **Exclusão**: Solicitar remoção de seus dados
- ✅ **Portabilidade**: Transferir seus dados
- ✅ **Revogação**: Retirar consentimento a qualquer momento

### **Contato para Exercício de Direitos**

Para exercer seus direitos LGPD, entre em contato:

- **Email**: privacidade@suaempresa.com
- **Prazo de resposta**: 15 dias úteis
- **Identificação**: Forneça dados suficientes para identificação

### **Medidas de Segurança**

- **Criptografia** em trânsito e repouso
- **Acesso restrito** apenas a pessoal autorizado
- **Monitoramento** de acessos e atividades
- **Backup seguro** com criptografia

### ⚖️ **Responsabilidades**

- **Controlador**: Empresa que utiliza o sistema
- **Operador**: Sistema MailMind (processamento técnico)
- **Titular**: Pessoa física proprietária dos dados

### **Consentimento**

**Ao utilizar este sistema, você concorda com:**

1. ✅ Processamento de dados pessoais conforme descrito
2. ✅ Uso de IA para análise e categorização
3. ✅ Geração de respostas automáticas quando aplicável
4. ✅ Encaminhamento para curadoria humana quando necessário

### **Notificação de Incidentes**

Em caso de incidente de segurança:

- **Detecção automática** de anomalias
- **Notificação imediata** aos responsáveis
- **Comunicação** aos titulares afetados (quando aplicável)
- **Relatório** à ANPD (quando necessário)

### **Relatórios de Conformidade**

- **Auditoria anual** de conformidade LGPD
- **Relatório de impacto** à proteção de dados
- **Documentação** de medidas de segurança

---

## **Implementação Técnica**

### **Avisos na Interface**

```html
<!-- Aviso de LGPD na interface -->
<div class="lgpd-notice">
  <h3>🛡️ Proteção de Dados</h3>
  <p>
    Este sistema está em conformidade com a LGPD. Seus dados são processados de
    forma segura e transparente.
  </p>
  <a href="/privacy-policy">Política de Privacidade</a>
</div>
```

### **Logs de Consentimento**

```python
# Log de consentimento LGPD
def log_consent(user_email, consent_type, timestamp):
    """Registra consentimento LGPD do usuário"""
    consent_log = {
        "email": user_email,
        "consent_type": consent_type,
        "timestamp": timestamp,
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent')
    }
    # Salvar em log seguro
```

### **API de Exercício de Direitos**

```python
@app.route('/lgpd/rights', methods=['POST'])
def exercise_lgpd_rights():
    """Endpoint para exercício de direitos LGPD"""
    data = request.get_json()
    right_type = data.get('right_type')  # access, correction, deletion, etc.
    user_email = data.get('email')

    # Processar solicitação conforme LGPD
    return jsonify({"status": "received", "deadline": "15 dias úteis"})
```

---

**Última atualização**: 03/01/2025  
**Status**: Conformidade LGPD implementada  
**Revisão**: Anual ou quando houver mudanças significativas
