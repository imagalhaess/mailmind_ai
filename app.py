#!/usr/bin/env python3
"""
Entry point for the Email Analyzer application.
"""
import sys
import os

# Adiciona o diretório app ao Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Importa e executa a aplicação
from app import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
