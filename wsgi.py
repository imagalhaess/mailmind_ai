# wsgi.py
from app import create_app

# Cria a instância da aplicação
app = create_app()

# Para compatibilidade com WSGI
application = app

if __name__ == "__main__":
    # Executa a aplicação quando o arquivo é chamado diretamente
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
