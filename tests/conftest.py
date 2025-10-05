"""
Configuração de fixtures para testes pytest.
"""
import pytest
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    """Cria uma instância da aplicação para testes."""
    # Define variáveis de ambiente para testes ANTES de importar
    os.environ['GEMINI_API_KEY'] = 'test-api-key-123'
    os.environ['ENVIRONMENT'] = 'testing'
    os.environ['CACHE_TYPE'] = 'SimpleCache'
    os.environ['RATE_LIMIT_ENABLED'] = 'false'  # Desabilita rate limiting em testes
    os.environ['SMTP_ENABLED'] = 'false'  # Desabilita SMTP em testes
    
    # Importa após configurar as variáveis de ambiente
    from app.app import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    
    yield app


@pytest.fixture
def client(app):
    """Cria um cliente de teste para a aplicação."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Cria um runner CLI para testes."""
    return app.test_cli_runner()


@pytest.fixture
def sample_email():
    """Email de exemplo para testes."""
    return """
From: teste@exemplo.com
Subject: Teste de Email

Este é um email de teste para validar o sistema de análise.
Por favor, responda quando possível.

Atenciosamente,
Equipe de Testes
"""


@pytest.fixture
def spam_email():
    """Email de spam para testes."""
    return """
From: spam@suspicious.com
Subject: GANHE DINHEIRO FÁCIL!!!

Você foi SELECIONADO para ganhar R$ 100.000,00!!!
Clique AQUI AGORA e receba seu prêmio!!!
URGENTE! Oferta válida apenas HOJE!!!
"""


@pytest.fixture
def batch_emails():
    """Múltiplos emails para testes de lote."""
    return """
From: cliente1@empresa.com
Subject: Proposta comercial

Gostaria de discutir uma parceria.

---

From: suporte@empresa.com
Subject: Problema técnico

Estou com dificuldades no sistema.

---

From: spam@bad.com
Subject: Oferta imperdível

Ganhe dinheiro rápido!
"""
