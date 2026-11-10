#!/usr/bin/env python3
import os
import json
import requests
import time
from datetime import datetime, timezone, timedelta

# ========================
# CONFIGURAÇÃO ÚNICA
# ========================
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL") or "<COLE_AQUI_SEU_WEBHOOK>"
API_URL = "https://ll.thespacedevs.com/2.0.0/launch/upcoming/?search=starship&ordering=net&limit=20"
SENT_FILE = os.getenv("SENT_FILE", "sent_launches.json")
WINDOW_DAYS = 7  # Quantos dias à frente considerar para publicação
CHECK_INTERVAL = 3600  # Intervalo entre verificações em segundos (1 hora)
DIAS_PT = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]

# Cores do embed por status
STATUS_COLORS = {
    "Go": 0x2ECC71,  # Verde
    "Hold": 0xF1C40F,  # Amarelo
    "Success": 0x3498DB,  # Azul
    "Failure": 0xE74C3C,  # Vermelho
    "TBD": 0x95A5A6,  # Cinza
    "Desconhecido": 0x7F8C8D,
}

# ========================
# FUNÇÕES AUXILIARES
# ========================


def iso_to_local(iso):
    """Converte ISO UTC para horário de Brasília em formato amigável"""
    if not iso:
        return "Sem data"
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    dt = datetime.fromisoformat(iso).astimezone(timezone.utc) - timedelta(hours=3)
    dia = DIAS_PT[dt.weekday()]
    return (
        f"{dia}, {dt.day:02d}/{dt.month:02d}/{dt.year} às {dt.hour:02d}:{dt.minute:02d}"
    )


def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_sent(sent):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(sent, f, indent=2, ensure_ascii=False)


def clean_sent(sent):
    """Remove lançamentos que já ocorreram"""
    now = datetime.now(timezone.utc)
    to_delete = []
    for launch_id, info in sent.items():
        net = info.get("net")
        if net:
            dt = datetime.fromisoformat(net.replace("Z", "+00:00"))
            if dt < now:
                to_delete.append(launch_id)
    for launch_id in to_delete:
        del sent[launch_id]
    return sent


def send_to_discord(embed):
    if "<COLE_AQUI_SEU_WEBHOOK>" in WEBHOOK_URL:
        print("⚠️ Configure seu webhook no topo do script ou na variável de ambiente DISCORD_WEBHOOK_URL")
        return False
    payload = {"username": "Rocket Bot", "embeds": [embed]}
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except requests.RequestException as e:
        print("Erro de rede ao enviar ao Discord:", e)
        return False
    if r.status_code >= 300:
        print("Erro ao enviar ao Discord:", r.text)
        return False
    print("✅ Mensagem enviada com sucesso.")
    return True


def format_launch_embed(launch, update=False):
    """Formata os dados do lançamento em um embed do Discord"""
    name = launch.get("name", "Sem nome")
    net = iso_to_local(launch.get("net", ""))
    pad = ((launch.get("pad") or {}).get("location") or {}).get("name") or "Desconhecido"
    status = (launch.get("status") or {}).get("name") or "Desconhecido"
    probability = launch.get("probability")
    rocket = (
        launch.get("rocket", {}).get("configuration", {}).get("name", "Desconhecido")
    )

    mission = launch.get("mission")
    if mission:
        mission_name = mission.get("name") or "Sem missão"
        mission_desc = mission.get("description") or "Sem descrição"
        mission_type = mission.get("type") or "Desconhecido"
        orbit = mission.get("orbit") or {}
        orbit_name = orbit.get("name") or "Desconhecido"
        mission_info = (
            f"**{mission_name}**\n{mission_type} – {orbit_name}\n{mission_desc}"
        )
    else:
        mission_info = "Sem missão"

    vids = launch.get("vidURLs", [])
    video = vids[0] if vids else "Sem transmissão"
    info_url = launch.get("info_url") or "N/A"

    # Escolhe cor pelo status
    color = STATUS_COLORS.get(status, 0x95A5A6)
    title_prefix = "🔄 Atualização:" if update else "🚀 Novo lançamento:"

    embed = {
        "title": f"{title_prefix} {name}",
        "color": color,
        "fields": [
            {"name": "🕓 Lançamento", "value": net, "inline": False},
            {"name": "📍 Local", "value": pad, "inline": False},
            {"name": "📡 Status", "value": status, "inline": True},
            {
                "name": "🎯 Probabilidade",
                "value": f"{probability}%" if probability is not None else "N/A",
                "inline": True,
            },
            {"name": "🚀 Foguete", "value": rocket, "inline": True},
            {"name": "🛰️ Missão", "value": mission_info[:1000], "inline": False},
            {"name": "🌐 Mais informações", "value": info_url, "inline": False},
            {"name": "📺 Transmissão", "value": video, "inline": False},
        ],
        "footer": {
            "text": f"Status: {status} | Última atualização: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}"
        },
    }

    return embed


# ========================
# MAIN
# ========================


def main():
    sent = load_sent()
    sent = clean_sent(sent)
    now = datetime.now(timezone.utc)

    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        launches = r.json().get("results", [])
    except Exception as e:
        print("Erro ao acessar a API:", e)
        return

    for launch in launches:
        launch_id = launch.get("id")
        net_iso = launch.get("net")
        if not net_iso:
            continue
        net_dt = datetime.fromisoformat(net_iso.replace("Z", "+00:00"))

        # Ignora lançamentos fora da janela de interesse
        if net_dt > now + timedelta(days=WINDOW_DAYS):
            continue

        status = (launch.get("status") or {}).get("name") or "Desconhecido"
        sent_info = sent.get(launch_id, {})
        sent_status = sent_info.get("status")
        sent_net = sent_info.get("net")

        # Envia lançamento novo confirmado
        if launch_id not in sent and status == "Go":
            embed = format_launch_embed(launch)
            if send_to_discord(embed):
                sent[launch_id] = {"status": status, "net": net_iso}
                print("🚀 Novo lançamento enviado:", launch.get("name"))
        # Envia atualização se status ou data mudarem
        elif launch_id in sent and (sent_status != status or sent_net != net_iso):
            embed = format_launch_embed(launch, update=True)
            if send_to_discord(embed):
                sent[launch_id] = {"status": status, "net": net_iso}
                print("🔄 Atualização enviada:", launch.get("name"))

    save_sent(sent)


if __name__ == "__main__":
    print("🤖 Rocket Bot iniciado. Verificando a cada 1 hora...")
    while True:
        print(f"🔍 Verificando lançamentos... {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}")
        try:
            main()
        except Exception as e:
            print("Erro inesperado na verificação:", e)
        print(f"💤 Aguardando {CHECK_INTERVAL // 60} minutos para a próxima verificação...")
        time.sleep(CHECK_INTERVAL)
