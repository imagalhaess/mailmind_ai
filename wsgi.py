#!/usr/bin/env python3
"""
WSGI entry point for the Email Analyzer application.
"""
import sys
import os

# Adiciona o diretório app ao Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação para WSGI
application = create_app()

if __name__ == "__main__":
    application.run()
