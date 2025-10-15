# Base Python leve
FROM python:3.12-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o script
COPY launch_to_discord.py .

# Variável de ambiente para o webhook (vai ser sobrescrita pelo -e no docker run)
ENV DISCORD_WEBHOOK_URL="<COLE_SEU_WEBHOOK_AQUI>"

# Comando padrão ao iniciar o container
CMD ["python", "/app/launch_to_discord.py"]

