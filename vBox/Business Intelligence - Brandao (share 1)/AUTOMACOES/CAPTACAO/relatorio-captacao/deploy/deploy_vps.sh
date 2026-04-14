#!/usr/bin/env bash
# deploy_vps.sh — Deploy do container captacao_relatorio na VPS
#
# Uso (a partir do diretório relatorio-captacao/deploy):
#   chmod +x deploy_vps.sh
#   ./deploy_vps.sh
#
# Pré-requisito local: chave SSH configurada para nobel@82.25.74.187

set -euo pipefail

VPS_USER="nobel"
VPS_HOST="82.25.74.187"
VPS_COMPOSE_DIR="/opt/postgres_v2/database"   # onde está o docker-compose na VPS
ASSESSOR_LOCAL="../../assessor.json"           # relativo a este script
ASSESSOR_REMOTE="/opt/captacao/assessor.json"

SSH="ssh ${VPS_USER}@${VPS_HOST}"

echo "========================================"
echo "Deploy captacao_relatorio → VPS"
echo "Host: ${VPS_HOST}"
echo "========================================"

# 1. Cria diretórios necessários na VPS
echo "[1/5] Criando diretórios na VPS..."
$SSH "mkdir -p /opt/captacao/logs"

# 2. Copia assessor.json para a VPS
echo "[2/5] Enviando assessor.json..."
scp "${ASSESSOR_LOCAL}" "${VPS_USER}@${VPS_HOST}:${ASSESSOR_REMOTE}"
echo "  → assessor.json enviado para ${ASSESSOR_REMOTE}"

# 3. Inicializa schema captacao no Postgres
echo "[3/5] Criando schema captacao no PostgreSQL..."
$SSH "docker exec -i postgres_nobel_v2 psql -U nobel_adm -d nobel_db" < ../deploy/init_captacao.sql
echo "  → Schema captacao inicializado."

# 4. Build + restart do container captacao_relatorio
echo "[4/5] Rebuild e restart do container..."
$SSH "cd ${VPS_COMPOSE_DIR} && \
    docker compose -f docker-compose.yml -f docker-compose.vps.yml \
        build captacao_relatorio && \
    docker compose -f docker-compose.yml -f docker-compose.vps.yml \
        up -d captacao_relatorio"

# 5. Mostra status
echo "[5/5] Status dos containers:"
$SSH "docker ps --filter name=captacao_relatorio --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "========================================"
echo "Deploy concluído!"
echo ""
echo "Para testar manualmente:"
echo "  ssh ${VPS_USER}@${VPS_HOST}"
echo "  docker exec captacao_relatorio python main.py"
echo ""
echo "Para ver logs do cron:"
echo "  docker exec captacao_relatorio tail -f /app/logs/cron.log"
echo "========================================"
