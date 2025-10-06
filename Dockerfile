# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

# Instala dependências do sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia apenas requirements para aproveitar cache do Docker
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Estágio final - imagem de produção
FROM python:3.11-slim

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Define diretório de trabalho
WORKDIR /app

# Copia dependências do estágio de build
COPY --from=builder /root/.local /home/appuser/.local

# Copia código da aplicação
COPY --chown=appuser:appuser . .

# Atualiza PATH para incluir binários do usuário
ENV PATH=/home/appuser/.local/bin:$PATH

# Muda para usuário não-root
USER appuser

# Expõe porta da aplicação
EXPOSE 8080

# Variáveis de ambiente padrão para Cloud Run
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)"

# Comando para iniciar a aplicação
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 300 --worker-class gthread --access-logfile - --error-logfile - wsgi:application
