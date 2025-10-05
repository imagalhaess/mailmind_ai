#!/bin/bash

# Script de deploy para Google Cloud Run
# Uso: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
PROJECT_ID=${1:-"mailmind-ai-474220"}
REGION=${2:-"us-central1"}
SERVICE_NAME="mailmind"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${GREEN}🚀 Iniciando deploy do MailMind para Google Cloud Run${NC}"
echo -e "${YELLOW}Projeto: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Região: ${REGION}${NC}"
echo ""

# Verifica se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI não encontrado. Instale em: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Verifica se está autenticado
echo -e "${YELLOW}📋 Verificando autenticação...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Não autenticado. Execute: gcloud auth login${NC}"
    exit 1
fi

# Define o projeto
echo -e "${YELLOW}🔧 Configurando projeto...${NC}"
gcloud config set project ${PROJECT_ID}

# Habilita APIs necessárias
echo -e "${YELLOW}🔌 Habilitando APIs necessárias...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Cria secrets no Secret Manager (se não existirem)
echo -e "${YELLOW}🔐 Configurando secrets...${NC}"

if ! gcloud secrets describe GEMINI_API_KEY --project=${PROJECT_ID} &> /dev/null; then
    echo -e "${YELLOW}Criando secret GEMINI_API_KEY...${NC}"
    if [ -f .env ]; then
        GEMINI_KEY=$(grep GEMINI_API_KEY .env | cut -d '=' -f2)
        echo -n "${GEMINI_KEY}" | gcloud secrets create GEMINI_API_KEY --data-file=- --project=${PROJECT_ID}
    else
        echo -e "${RED}⚠️  Arquivo .env não encontrado. Crie o secret manualmente.${NC}"
    fi
fi

# Build da imagem
echo -e "${YELLOW}🏗️  Construindo imagem Docker...${NC}"
gcloud builds submit --tag ${IMAGE_NAME} --project=${PROJECT_ID}

# Deploy para Cloud Run
echo -e "${YELLOW}🚢 Fazendo deploy para Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --timeout 300 \
    --set-env-vars ENVIRONMENT=production,PORT=8080 \
    --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
    --project=${PROJECT_ID}

# Obtém URL do serviço
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)' --project=${PROJECT_ID})

echo ""
echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo -e "${GREEN}🌐 URL do serviço: ${SERVICE_URL}${NC}"
echo -e "${GREEN}🏥 Health check: ${SERVICE_URL}/health${NC}"
echo ""
echo -e "${YELLOW}📊 Para ver logs:${NC}"
echo -e "   gcloud run services logs read ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID}"
echo ""
echo -e "${YELLOW}📈 Para ver métricas:${NC}"
echo -e "   https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
