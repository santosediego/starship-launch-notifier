# Starship Launch Notifier 🚀

Bot simples que envia notificações de lançamentos confirmados da Starship direto para um canal do Discord via webhook.

Este projeto é feito para rodar **24/7 em Docker**, sem histórico ou armazenamento persistente, apenas notificando quando há lançamentos relevantes.

Dados de lançamentos são obtidos da **[The Space Devs API](https://thespacedevs.com/)**.

---

## ⚙️ Estrutura do Projeto

```
starship-launcher/
├── launch_to_discord.py   # Código principal do bot
├── requirements.txt      # Dependências Python
├── Dockerfile            # Definição do container
```

> **OBS:** Nenhum arquivo contém dados sensíveis. O webhook do Discord deve ser passado via **variável de ambiente**.

---

## 🐍 Dependências

* Python 3.12+
* requests

As dependências são instaladas automaticamente ao buildar o container via Docker.

---

## 🐳 Rodando com Docker

### 1️⃣ Build da imagem

```bash
docker build -t starship-launcher .
```

### 2️⃣ Rodar container em background (24/7)

```bash
docker run -d --restart unless-stopped \
    --name starship-launcher \
    -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI" \
    starship-launcher
```

* `-d` → roda em background
* `--restart unless-stopped` → sobe automaticamente se a VM reiniciar
* `-e DISCORD_WEBHOOK_URL=...` → webhook do Discord

### 3️⃣ Comandos úteis

* Parar container:

```bash
docker stop starship-launcher
```

* Remover container:

```bash
docker rm starship-launcher
```

* Ver logs:

```bash
docker logs -f starship-launcher
```
