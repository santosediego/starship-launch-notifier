# Starship Launch Notifier 🚀

[![Licença](https://img.shields.io/github/license/santosediego/starship-launch-notifier?style=for-the-badge)](https://github.com/santosediego/starship-launch-notifier/blob/main/LICENSE)

![Python](https://img.shields.io/badge/python_3.12-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%232496ED.svg?style=for-the-badge&logo=docker&logoColor=white)
![Discord](https://img.shields.io/badge/discord_webhook-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

## Sobre o projeto

Bot simples que avisa em um canal do Discord quando um lançamento da **Starship** (SpaceX) é confirmado. Ele roda 24/7 em um container Docker e usa um **webhook** do Discord, então não precisa criar um bot nem dar permissões a ele.

Os dados vêm da [The Space Devs API](https://thespacedevs.com/ "The Space Devs").

## Como funciona

A cada **1 hora**, o bot consulta a API e olha os lançamentos da Starship previstos para os **próximos 7 dias**:

- Quando um lançamento passa a ter o status **Go** (confirmado), ele envia um aviso novo (🚀).
- Se um lançamento já avisado mudar de **status ou de horário** (por exemplo, entrar em *Hold* ou adiar), ele envia uma atualização (🔄).
- Lançamentos ainda em *TBD* são ignorados, e os que já passaram são esquecidos.

Cada mensagem traz o horário já convertido para **Brasília**, o local, o status, a probabilidade, o foguete, a missão, o link de mais informações e o da transmissão. A cor da mensagem muda conforme o status (verde para Go, amarelo para Hold e assim por diante).

Para não repetir avisos, o bot guarda os lançamentos já enviados em um pequeno arquivo (`sent_launches.json`). Se o Discord recusar o envio, o lançamento **não** é marcado como enviado, e ele tenta de novo na verificação seguinte.

## Tecnologias utilizadas

- Python 3.12
- Requests
- Docker
- Webhook do Discord (embeds)
- The Space Devs API (Launch Library 2)

## Como executar o projeto

### Criando o webhook no Discord

1. No canal que vai receber os avisos, abra **Configurações do canal → Integrações → Webhooks**.
2. Clique em **Novo webhook** e copie a URL.

> A URL do webhook é uma **senha**: quem a tiver consegue postar no seu canal. Não a coloque no código nem no GitHub. Se vazar, apague o webhook e crie outro.

### Com Docker (recomendado)

Pré-requisito: Docker.

```bash
# clonar repositório
git clone https://github.com/santosediego/starship-launch-notifier.git

# entrar na pasta do projeto
cd starship-launch-notifier

# construir a imagem
docker build -t starship-launcher .
```

Guarde o webhook em um arquivo **fora do projeto**, com uma linha só (sem aspas e sem espaços em volta do `=`):

```bash
nano ~/.env.discord
```

```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/SEU_ID/SEU_TOKEN
```

```bash
chmod 600 ~/.env.discord
```

Suba o container em segundo plano:

```bash
docker run -d --restart unless-stopped \
    --name starship-launcher \
    --env-file ~/.env.discord \
    -e SENT_FILE=/data/sent_launches.json \
    -v starship-data:/data \
    starship-launcher
```

| Opção | O que faz |
|-------|-----------|
| `-d` | Roda em segundo plano |
| `--restart unless-stopped` | Sobe de novo se o servidor reiniciar |
| `--env-file` | Lê o webhook do arquivo, sem deixá-lo no histórico do terminal |
| `-e SENT_FILE` e `-v` | Guardam a lista de avisos enviados em um volume, para ela sobreviver caso o container seja recriado |

Sem o volume, o bot funciona do mesmo jeito, mas, se você apagar e recriar o container, a lista se perde e ele pode reenviar avisos de lançamentos já confirmados.

### Comandos úteis

```bash
# ver os logs (deve aparecer uma verificação por hora)
docker logs -f starship-launcher

# ver o que já foi enviado
docker exec starship-launcher cat /data/sent_launches.json

# parar e remover o container
docker stop starship-launcher
docker rm starship-launcher
```

### Sem Docker

Pré-requisitos: Python 3.12 e o `pip`.

```bash
pip install -r requirements.txt
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/SEU_ID/SEU_TOKEN"
python launch_to_discord.py
```

### Testando o webhook

Para conferir se o canal recebe mensagens, sem esperar um lançamento:

```bash
curl -H "Content-Type: application/json" \
     -d '{"content":"teste do Rocket Bot"}' \
     "SUA_URL_DO_WEBHOOK"
```

## Estrutura do projeto

```
starship-launch-notifier/
├── launch_to_discord.py   # Código do bot
├── requirements.txt       # Dependências Python
├── Dockerfile             # Definição do container
├── README.md
└── LICENSE
```

## Limitações conhecidas

- O bot só avisa lançamentos que a API marca como **Go**. Se o status ficar em *TBD* até muito perto do voo, o aviso sai tarde, em até 1 hora depois da mudança.
- Depende da The Space Devs API. A versão gratuita tem limite de requisições por hora (a de 1 por hora usada aqui fica bem abaixo) e pode ficar fora do ar. Quando isso acontece, o bot só registra o erro no log e tenta de novo na próxima verificação.
- Só acompanha lançamentos da Starship, na janela de 7 dias.
- Mensagens em português, com o horário fixo em Brasília (UTC-3).

## Autor

[Diego Santos](https://www.linkedin.com/in/santosediego/ "Perfil Linkedin Diego Santos")