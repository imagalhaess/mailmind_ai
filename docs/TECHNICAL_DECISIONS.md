# Decisões Técnicas - MailMind AI

**Versão**: 2.1.0  
**Última atualização**: 05/10/2025  
**Autor**: Isabela Mattos (desenvolvimento) | Manus AI (refatoração v2.0 para deploy com Google Cloud)

Este documento registra as principais decisões técnicas do projeto MailMind AI, explicando o **porquê** de cada escolha e as alternativas consideradas. O objetivo é facilitar a compreensão do projeto para novos desenvolvedores e manter a consistência nas futuras evoluções.

---

## Decisão 1: Modelo de IA - Google Gemini

### Escolha: Google Gemini 2.5 Flash

**Motivação**:

- **Custo-benefício**: Gemini Flash oferece excelente performance a um custo muito inferior ao GPT-4 da OpenAI.
- **Latência**: Respostas rápidas (1-3 segundos) adequadas para análise de emails.
- **Capacidade**: Suporta contextos longos (até 1 milhão de tokens), ideal para emails extensos.
- **JSON nativo**: Suporte nativo a respostas estruturadas em JSON, reduzindo parsing errors.

**Alternativas Consideradas**:

- **OpenAI GPT-4**: Rejeitado devido ao custo elevado (~10x mais caro).
- **Claude (Anthropic)**: Rejeitado devido à complexidade de integração e custo.
- **Modelos open-source (LLaMA, Mistral)**: Rejeitado devido à necessidade de infraestrutura própria.

**Implicações**:

- ✅ Custo operacional baixo (~$0.10 por 1000 requisições).
- ✅ Integração simples via biblioteca oficial `google-generativeai`.
- ⚠️ Dependência de serviço externo (Google Cloud).

---

## Decisão 2: Framework Web - Flask

### Escolha: Flask com Gunicorn

**Motivação**:

- **Simplicidade**: Flask é minimalista e fácil de entender, ideal para um projeto focado.
- **Flexibilidade**: Permite estruturar o código de forma modular sem imposições rígidas.
- **Ecossistema**: Extensões maduras para cache (Flask-Caching), rate limiting (Flask-Limiter) e CORS (Flask-CORS).
- **Performance**: Com Gunicorn e workers, suporta centenas de requisições simultâneas.

**Alternativas Consideradas**:

- **FastAPI**: Rejeitado devido à curva de aprendizado (async/await) e complexidade desnecessária para o caso de uso.
- **Django**: Rejeitado por ser muito pesado para uma aplicação de análise de emails.

**Implicações**:

- ✅ Código limpo e fácil de manter.
- ✅ Deploy simples em contêineres Docker.
- ⚠️ Requer Gunicorn para produção (Flask dev server não é adequado).

---

## Decisão 3: Arquitetura - Clean Architecture Simplificada

### Escolha: Separação em camadas (Providers, Services, Utils)

**Motivação**:

- **Manutenibilidade**: Código organizado por responsabilidade facilita manutenção e testes.
- **Testabilidade**: Camadas desacopladas permitem testes unitários isolados.
- **Escalabilidade**: Fácil adicionar novos provedores de IA ou serviços sem afetar o resto do código.

**Estrutura Implementada**:

```
app/
├── providers/       # Clientes de serviços externos (Gemini)
├── services/        # Lógica de negócio (análise de emails)
├── utils/           # Funções utilitárias (preprocessamento, email)
└── app.py           # Rotas e configuração da aplicação
```

**Alternativas Consideradas**:

- **Monolito único**: Rejeitado devido à dificuldade de manutenção.
- **Microserviços**: Rejeitado por adicionar complexidade desnecessária para o escopo atual.

**Implicações**:

- ✅ Código organizado e fácil de navegar.
- ✅ Testes isolados por camada.
- ⚠️ Requer disciplina para manter a separação de responsabilidades.

---

## Decisão 4: Configuração - Variáveis de Ambiente (.env)

### Escolha: Dataclass centralizada + python-dotenv

**Motivação**:

- **Segurança**: Credenciais sensíveis (API keys) não ficam no código.
- **Flexibilidade**: Fácil alterar configurações entre ambientes (dev, prod).
- **Validação**: Dataclass com type hints garante que as configurações estão corretas.

**Implementação**:

```python
@dataclass
class Config:
    gemini_api_key: str
    model_name: str = "gemini-2.5-flash"
    # ... outras configs
```

**Alternativas Consideradas**:

- **Arquivo de configuração (config.yaml)**: Rejeitado devido à complexidade adicional.
- **Variáveis de ambiente diretas**: Rejeitado devido à falta de validação.

**Implicações**:

- ✅ Configuração centralizada e validada.
- ✅ Fácil integração com Docker e Cloud Run.
- ⚠️ Requer arquivo `.env` para desenvolvimento local.

---

## Decisão 5: Cache - Redis com Fallback para SimpleCache

### Escolha: Flask-Caching com Redis em produção

**Motivação**:

- **Performance**: Cache reduz latência de 2-3s para <100ms em requisições repetidas.
- **Custo**: Reduz chamadas à API do Gemini em 30-50%, economizando dinheiro.
- **Flexibilidade**: SimpleCache (memória) para desenvolvimento sem necessidade de Redis.

**Implementação**:

- Cache baseado em hash SHA-256 do conteúdo do email.
- TTL padrão de 24 horas (configurável).

**Alternativas Consideradas**:

- **Sem cache**: Rejeitado devido ao custo e latência elevados.
- **Cache em disco**: Rejeitado devido à complexidade e problemas de concorrência.

**Implicações**:

- ✅ Performance significativamente melhorada.
- ✅ Economia de custos com API.
- ⚠️ Requer Redis em produção (incluído no docker-compose).

---

## Decisão 6: Segurança - Rate Limiting + API Keys

### Escolha: Flask-Limiter + Validação de API Key opcional

**Motivação**:

- **Proteção contra abuso**: Rate limiting evita ataques de força bruta e uso excessivo.
- **Controle de acesso**: API Keys permitem restringir acesso a endpoints críticos (webhook).
- **Flexibilidade**: Rate limiting pode ser desabilitado em desenvolvimento.

**Limites Implementados**:

- `/analyze`: 20 requisições por minuto
- `/webhook/email`: 30 requisições por minuto
- `/test/*`: 60 requisições por minuto

**Alternativas Consideradas**:

- **Sem rate limiting**: Rejeitado devido ao risco de abuso.
- **OAuth2**: Rejeitado por adicionar complexidade desnecessária para o caso de uso.

**Implicações**:

- ✅ Aplicação protegida contra abuso.
- ✅ Controle de acesso granular.
- ⚠️ Requer Redis para rate limiting distribuído em produção.

---

## Decisão 7: Testes - Pytest com Cobertura

### Escolha: Pytest + pytest-flask + pytest-cov

**Motivação**:

- **Qualidade**: Testes automatizados garantem que alterações não quebram funcionalidades existentes.
- **Confiança**: Cobertura de 63% (e crescendo) garante que o código crítico está testado.
- **Simplicidade**: Pytest é intuitivo e tem excelente suporte para Flask.

**Estrutura de Testes**:

```
tests/
├── conftest.py              # Fixtures compartilhadas
├── test_app.py              # Testes de rotas
├── test_email_analyzer.py   # Testes de serviços
└── test_utils.py            # Testes de utilitários
```

**Alternativas Consideradas**:

- **Unittest**: Rejeitado devido à verbosidade.
- **Sem testes**: Rejeitado devido ao risco de regressões.

**Implicações**:

- ✅ Código mais confiável e manutenível.
- ✅ Facilita refatorações futuras.
- ⚠️ Requer disciplina para manter testes atualizados.

---

## Decisão 8: Containerização - Docker Multi-Stage Build

### Escolha: Dockerfile otimizado com multi-stage build

**Motivação**:

- **Tamanho**: Multi-stage build reduz o tamanho da imagem em ~40%.
- **Segurança**: Usuário não-root (appuser) reduz superfície de ataque.
- **Reprodutibilidade**: Ambiente idêntico em dev, staging e produção.

**Otimizações Implementadas**:

- Build stage separado para compilação de dependências.
- Camadas ordenadas para maximizar cache do Docker.
- Health check integrado para monitoramento.

**Alternativas Consideradas**:

- **Dockerfile simples**: Rejeitado devido ao tamanho da imagem.
- **Imagem Alpine**: Rejeitado devido a problemas de compatibilidade com algumas bibliotecas Python.

**Implicações**:

- ✅ Imagem otimizada (~200MB vs ~500MB).
- ✅ Deploy rápido no Cloud Run.
- ⚠️ Build inicial mais lento (~3-5 minutos).

---

## Decisão 9: Deploy - Google Cloud Run

### Escolha: Cloud Run com Cloud Build para CI/CD

**Motivação**:

- **Simplicidade**: Deploy com um comando (`gcloud run deploy`).
- **Escalabilidade**: Auto-scaling de 0 a 10 instâncias conforme demanda.
- **Custo**: Pay-per-use, ideal para aplicações com tráfego variável.
- **Integração**: Integração nativa com Secret Manager para credenciais.

**Configuração**:

- Memória: 512Mi
- CPU: 1 vCPU
- Timeout: 300s
- Min instances: 0 (cold start aceitável)
- Max instances: 10

**Alternativas Consideradas**:

- **Heroku**: Rejeitado devido ao custo elevado e limitações.
- **AWS Lambda**: Rejeitado devido à complexidade de configuração.
- **Kubernetes**: Rejeitado por ser overkill para o escopo atual.

**Implicações**:

- ✅ Deploy simples e rápido.
- ✅ Custo baixo (~$0-5/mês para uso moderado).
- ⚠️ Cold start de ~2-3s na primeira requisição.

---

## Decisão 10: Lógica de Classificação - Produtivo vs Improdutivo

### Escolha: Apenas Spam e Erro são improdutivos

**Motivação**:

- **Clareza**: Classificação binária simples facilita decisões de negócio.
- **Segurança**: Spam não recebe resposta automática (evita confirmar recebimento).
- **Flexibilidade**: Consultas, Reclamações e Urgentes são produtivos e recebem atenção.

**Categorias Implementadas**:

- **Improdutivos**: Spam, Erro
- **Produtivos**: Produtivo, Consulta, Reclamação, Urgente, Outro

**Alternativas Consideradas**:

- **Todas as categorias como improdutivas**: Rejeitado por perder nuances importantes.
- **Classificação multi-nível**: Rejeitado por adicionar complexidade desnecessária.

**Implicações**:

- ✅ Interface clara para o usuário.
- ✅ Lógica de negócio simples e compreensível.
- ⚠️ Requer prompt bem definido para o Gemini classificar corretamente.

---

## Decisões Futuras Planejadas

### Curto Prazo (1-3 meses)

- **Processamento Assíncrono**: Celery + Redis para análise de lotes grandes.
- **Dashboard de Analytics**: Métricas de uso, categorias mais comuns, etc.
- **Integração com Gmail/Outlook**: Análise automática de caixa de entrada.

### Médio Prazo (3-6 meses)

- **Fine-tuning do Gemini**: Modelo customizado com feedback dos usuários.
- **Multi-idioma**: Suporte a inglês, espanhol, etc.
- **API pública**: Permitir integração com outros sistemas.

### Longo Prazo (6-12 meses)

- **Machine Learning local**: Modelo próprio para reduzir dependência de APIs externas.
- **Análise de sentimento**: Detectar urgência e tom do email.
- **Resposta automática inteligente**: Gerar respostas personalizadas.

---

## Resumo das Decisões

| Aspecto           | Decisão                          | Motivação Principal        |
| ----------------- | -------------------------------- | -------------------------- |
| **IA**            | Google Gemini 2.5 Flash          | Custo-benefício            |
| **Framework**     | Flask + Gunicorn                 | Simplicidade e performance |
| **Arquitetura**   | Clean Architecture               | Manutenibilidade           |
| **Configuração**  | .env + Dataclass                 | Segurança e validação      |
| **Cache**         | Redis (prod) / SimpleCache (dev) | Performance e custo        |
| **Segurança**     | Rate Limiting + API Keys         | Proteção contra abuso      |
| **Testes**        | Pytest + cobertura               | Qualidade e confiança      |
| **Container**     | Docker multi-stage               | Tamanho e segurança        |
| **Deploy**        | Google Cloud Run                 | Simplicidade e custo       |
| **Classificação** | Binária (Prod/Improd)            | Clareza e segurança        |

---

**Contribuições**: Se você tem sugestões de melhorias ou questiona alguma decisão, abra uma issue no GitHub para discutirmos!
