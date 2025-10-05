# wsgi.py
from app import create_app

# Cria a instância da aplicação
app = create_app()

# Para compatibilidade com WSGI
application = app

if __name__ == "__main__":
    app.run()