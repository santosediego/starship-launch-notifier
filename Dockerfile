# Base Python leve
FROM python:3.12-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o script
COPY launch_to_discord.py .

# Python sem buffer, para o docker logs mostrar a saída na hora
ENV PYTHONUNBUFFERED=1

# Comando padrão ao iniciar o container
CMD ["python", "/app/launch_to_discord.py"]

