# Guia de Desenvolvimento - MailMind

## Início Rápido

### 1. **Configuração do Ambiente**

```bash
# Clone o repositório
git clone <repository-url>
cd mailmind

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2. **Configuração das Variáveis**

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com suas credenciais
nano .env
```

**Variáveis obrigatórias**:

```env
GEMINI_API_KEY=sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_de_app
NOREPLY_ADDRESS=seu_email@gmail.com
CURATOR_ADDRESS=curador@empresa.com
```

### 3. **Execução**

```bash
# Desenvolvimento
python app.py

# Produção (com Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

## Desenvolvimento

### **Convenções de Código**

#### **Python**

- **PEP 8**: Seguir padrões de estilo Python
- **Type Hints**: Usar onde possível
- **Docstrings**: Documentar funções públicas
- **Imports**: Organizar (stdlib, third-party, local)

#### **Nomenclatura**

```python
# Classes: PascalCase
class EmailAnalyzerService:
    pass

# Funções: snake_case
def analyze_email(content: str) -> dict:
    pass

# Constantes: UPPER_CASE
GEMINI_API_KEY = "sua_chave"

# Variáveis: snake_case
email_content = "conteúdo do email"
```

#### **Estrutura de Funções**

```python
def exemplo_funcao(parametro: str) -> dict:
    """
    Descrição clara do que a função faz.

    Args:
        parametro: Descrição do parâmetro

    Returns:
        dict: Descrição do retorno

    Raises:
        ValueError: Quando o parâmetro é inválido
    """
    # Validação de entrada
    if not parametro:
        raise ValueError("Parâmetro não pode ser vazio")

    # Lógica principal
    resultado = processar_parametro(parametro)

    # Retorno
    return resultado
```

### **Padrões de Arquitetura**

#### **1. Separation of Concerns**

```python
# ❌ Ruim: Tudo misturado
def processar_email(email):
    # Validação
    if not email:
        return None

    # Chamada da API
    response = requests.post("https://api.gemini.com", data=email)

    # Envio de email
    smtp.send("resposta@empresa.com", "Resposta automática")

    # Log
    print(f"Email processado: {email}")

# ✅ Bom: Responsabilidades separadas
class EmailAnalyzerService:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    def analyze(self, email_content: str) -> dict:
        return self.gemini_client.generate_content(email_content)

class EmailSender:
    def send(self, to: str, subject: str, body: str) -> bool:
        # Lógica de envio
        pass
```

#### **2. Dependency Injection**

```python
# ❌ Ruim: Dependência hardcoded
class EmailAnalyzerService:
    def __init__(self):
        self.gemini_client = GeminiClient("chave_hardcoded")

# ✅ Bom: Dependência injetada
class EmailAnalyzerService:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
```

#### **3. Error Handling**

```python
# ❌ Ruim: Erro silencioso
def processar_email(email):
    try:
        resultado = api_call(email)
        return resultado
    except:
        return None

# ✅ Bom: Tratamento explícito
def processar_email(email: str) -> dict:
    try:
        resultado = api_call(email)
        return resultado
    except APITimeoutError as e:
        logging.error(f"Timeout na API: {e}")
        raise ProcessingError("Falha temporária na análise")
    except APIError as e:
        logging.error(f"Erro na API: {e}")
        raise ProcessingError("Falha na análise do email")
```

### **Testes**

#### **Estrutura de Testes**

```python
# app/tests/ (arquivos de teste disponíveis)
import pytest
from unittest.mock import Mock, patch
from services.email_analyzer import EmailAnalyzerService

class TestEmailAnalyzer:
    def setup_method(self):
        """Setup para cada teste."""
        self.mock_gemini = Mock()
        self.service = EmailAnalyzerService(self.mock_gemini)

    def test_analyze_success(self):
        """Testa análise bem-sucedida."""
        # Arrange
        email_content = "Email de teste"
        expected_result = {"categoria": "Spam", "atencao_humana": "NÃO"}
        self.mock_gemini.generate_content.return_value = expected_result

        # Act
        result = self.service.analyze(email_content)

        # Assert
        assert result == expected_result
        self.mock_gemini.generate_content.assert_called_once_with(email_content)

    def test_analyze_api_error(self):
        """Testa erro na API."""
        # Arrange
        self.mock_gemini.generate_content.side_effect = Exception("API Error")

        # Act & Assert
        with pytest.raises(Exception):
            self.service.analyze("test")
```

#### **Executando Testes**

```bash
# Executar todos os testes
pytest

# Executar com coverage
pytest --cov=services --cov=providers --cov=utils

# Executar teste específico
pytest app/tests/  # Executar testes disponíveis
```

### **Logging**

#### **Configuração de Logs**

```python
import logging

# Configuração básica
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Uso nos serviços
def processar_email(email: str):
    logger.info(f"Processando email de: {email[:50]}...")

    try:
        resultado = analisar(email)
        logger.info(f"Email processado com sucesso: {resultado['categoria']}")
        return resultado
    except Exception as e:
        logger.error(f"Erro ao processar email: {e}")
        raise
```

## Fluxo de Desenvolvimento

### **1. Nova Funcionalidade**

```bash
# 1. Criar branch
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver
# - Implementar código
# - Adicionar testes
# - Atualizar documentação

# 3. Testar
pytest
python app.py  # Teste manual

# 4. Commit
git add .
git commit -m "feat: adiciona nova funcionalidade"

# 5. Push
git push origin feature/nova-funcionalidade

# 6. Pull Request
# - Criar PR no GitHub
# - Revisar código
# - Merge após aprovação
```

### **2. Correção de Bug**

```bash
# 1. Criar branch
git checkout -b fix/corrige-bug-x

# 2. Reproduzir bug
# - Identificar causa
# - Criar teste que falha

# 3. Corrigir
# - Implementar correção
# - Verificar que teste passa

# 4. Commit
git commit -m "fix: corrige bug na análise de emails"

# 5. Push e PR
```

### **3. Refatoração**

```bash
# 1. Criar branch
git checkout -b refactor/melhora-arquitetura

# 2. Refatorar
# - Melhorar código
# - Manter funcionalidade
# - Adicionar testes

# 3. Commit
git commit -m "refactor: melhora arquitetura do serviço de análise"

# 4. Push e PR
```

## Testes e Qualidade

### **Tipos de Testes**

#### **1. Testes Unitários**

```python
# Testa uma função/método isoladamente
def test_extract_sender():
    email = "From: joao@empresa.com\nSubject: Teste\n\nConteúdo"
    sender = extract_sender_from_email(email)
    assert sender == "joao@empresa.com"
```

#### **2. Testes de Integração**

```python
# Testa integração entre componentes
def test_webhook_integration():
    response = client.post('/webhook/email', json={
        'sender': 'test@test.com',
        'subject': 'Teste',
        'email_content': 'Conteúdo de teste'
    })
    assert response.status_code == 200
```

#### **3. Testes de Aceitação**

```python
# Testa fluxo completo do usuário
def test_email_analysis_flow():
    # 1. Usuário envia email
    # 2. Sistema analisa
    # 3. Sistema executa ação
    # 4. Usuário vê resultado
    pass
```

### **Ferramentas de Qualidade**

#### **Linting**

```bash
# Instalar
pip install flake8 black isort

# Executar
flake8 .                    # Verificar estilo
black .                     # Formatar código
isort .                     # Organizar imports
```

#### **Type Checking**

```bash
# Instalar
pip install mypy

# Executar
mypy .                      # Verificar tipos
```

#### **Security**

```bash
# Instalar
pip install bandit safety

# Executar
bandit -r .                 # Verificar vulnerabilidades
safety check               # Verificar dependências
```

## Deploy

### **Desenvolvimento**

```bash
python app.py
```

### **Produção**

```bash
# Com Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()

# Com Docker (futuro)
docker build -t email-analyzer .
docker run -p 8000:8000 email-analyzer
```

### **Variáveis de Ambiente**

#### **Desenvolvimento**

```env
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

#### **Produção**

```env
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO
```

## Recursos Úteis

### **Documentação**

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Gemini API](https://ai.google.dev/)
- [pytest Documentation](https://docs.pytest.org/)

### **Ferramentas**

- [Postman](https://www.postman.com/) - Testar APIs
- [Insomnia](https://insomnia.rest/) - Alternativa ao Postman
- [VS Code](https://code.visualstudio.com/) - Editor recomendado

### **Extensões VS Code**

- Python
- Python Docstring Generator
- GitLens
- Thunder Client (para testar APIs)

## Troubleshooting

### **Problemas Comuns**

#### **1. Erro de Import**

```bash
# Problema: ModuleNotFoundError
# Solução: Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### **2. Erro de Gemini API**

```bash
# Problema: 401 Unauthorized
# Solução: Verificar GEMINI_API_KEY no .env
```

#### **3. Erro de SMTP**

```bash
# Problema: Connection refused
# Solução: Verificar credenciais SMTP
# Gmail: Usar senha de app, não senha normal
```

#### **4. Porta em Uso**

```bash
# Problema: Address already in use
# Solução: Mudar porta ou matar processo
lsof -ti:8001 | xargs kill -9
```

---

**Última atualização**: 03/01/2025  
**Versão**: 1.0.0  
**Status**: Guia completo para desenvolvimento
