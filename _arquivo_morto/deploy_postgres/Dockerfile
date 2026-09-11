FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema (cron + locales para UTF-8)
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron locales \
    && sed -i 's/# pt_BR.UTF-8/pt_BR.UTF-8/' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=pt_BR.UTF-8
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUTF8=1

# Instala dependências Python (sem pywin32 — não disponível no Linux)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    pandas openpyxl numpy matplotlib requests psycopg2-binary \
    python-dotenv

# Copia código-fonte
COPY . .

# Cria diretório de logs
RUN mkdir -p /app/logs

# Configura cron
COPY deploy/crontab /etc/cron.d/captacao
RUN chmod 0644 /etc/cron.d/captacao \
    && crontab /etc/cron.d/captacao

CMD ["cron", "-f"]
