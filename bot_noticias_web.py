import requests
import time
import random
import threading
import os
from datetime import datetime, timedelta
from flask import Flask

# Configurações do bot
TELEGRAM_TOKEN = '8067274719:AAEWHOSwqquzP3qvhBKZryM7QfTMEAbMPhg'
CHAT_ID = '-1002562674482'
NEWS_API_KEYS = [
    'a60a973857b04b42b913db4261ed35c5',
    'api_live_Cp60aT3qJHcIe9XUMUdWgw4oN6gsj1w3b0C1enraytddWmHpgpY0Rctu'
]
ENVIADAS = set()

# Mensagens motivacionais (mantidas exatamente como no original)
mensagens_bom_dia = [
    "🌞 Bom dia! Descubra hoje como a IA e o mundo cripto estão mudando o mundo!\n👉 https://t.me/rafaelsheikIA",
    "🧠 Comece o dia aprendendo algo novo com as maiores inovações!\n👉 https://t.me/rafaelsheikIA"
]
mensagens_boa_tarde = [
    "🌤 Boa tarde! Mantenha o foco nos seus objetivos com tecnologia e liberdade financeira!\n👉 https://t.me/rafaelsheikIA",
    "💻 Que sua tarde seja tão produtiva quanto um algoritmo bem treinado!\n👉 https://t.me/rafaelsheikIA"
]
mensagens_boa_noite = [
    "🌙 Boa noite! Enquanto o mundo dorme, a inovação não para. Fique por dentro!\n👉 https://t.me/rafaelsheikIA",
    "✨ Que sua noite seja tranquila e sua mente cheia de ideias brilhantes!\n👉 https://t.me/rafaelsheikIA"
]

# Flask app apenas para manter o serviço ativo (não interfere no bot)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Notícias Online"

@app.route('/status')
def status():
    return {"status": "online", "enviadas": len(ENVIADAS)}

# Funções originais do bot (sem alterações)
def enviar_mensagem(mensagem):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML'}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def buscar_noticias_newsapi(topico):
    try:
        url = f'https://newsapi.org/v2/everything?q={topico}&language=pt&apiKey={NEWS_API_KEYS[0]}'
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            return resposta.json().get('articles', [])
    except Exception as e:
        print(f"Erro NewsAPI: {e}")
    return []

def buscar_noticias_newsdata(topico):
    try:
        url = f'https://newsdata.io/api/1/news?apikey={NEWS_API_KEYS[1]}&q={topico}&language=pt'
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            return resposta.json().get('results', [])
    except Exception as e:
        print(f"Erro NewsData: {e}")
    return []

def nova_noticia(lista):
    for noticia in lista:
        url = noticia.get('url') or noticia.get('link')
        if url and url not in ENVIADAS:
            ENVIADAS.add(url)
            titulo = noticia.get('title', 'Sem título')
            return f"🗞 <b>{titulo}</b>\n{url}"
    return None

def buscar_cotacoes():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl,eur'
        r = requests.get(url, timeout=10)
        data = r.json()
        btc = data['bitcoin']
        eth = data['ethereum']
        dolar = btc['usd'] / btc['brl']
        euro = btc['eur'] / btc['brl']
        msg = (
            f"💸 <b>COTAÇÕES ATUAIS</b>\n"
            f"🪙 Bitcoin: ${btc['usd']:,} | R${btc['brl']:,}\n"
            f"⛓ Ethereum: ${eth['usd']:,} | R${eth['brl']:,}\n"
            f"💵 Dólar: R${dolar:.2f} | 💶 Euro: R${euro:.2f}"
        )
        return msg
    except Exception as e:
        print(f"Erro cotação: {e}")
        return None

def enviar_motivacional():
    hora = datetime.now().hour
    if 6 <= hora < 12:
        mensagem = random.choice(mensagens_bom_dia)
    elif 12 <= hora < 18:
        mensagem = random.choice(mensagens_boa_tarde)
    elif 18 <= hora < 24:
        mensagem = random.choice(mensagens_boa_noite)
    else:
        mensagem = random.choice(mensagens_bom_dia)
    enviar_mensagem(mensagem)

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    # Iniciar Flask em thread separada (apenas para manter o serviço ativo)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Loop principal do bot (exatamente como no original)
    ultima_cotacao = datetime.now() - timedelta(hours=1)
    ultima_noticia = datetime.now() - timedelta(minutes=30)
    ultima_motivacional = datetime.now() - timedelta(hours=2)

    noticia_topicos = ['inteligência artificial', 'criptomoeda', 'tecnologia']
    indice_topico = 0

    while True:
        agora = datetime.now()

        if agora - ultima_cotacao >= timedelta(hours=1):
            cotacao = buscar_cotacoes()
            if cotacao:
                enviar_mensagem(cotacao)
            ultima_cotacao = agora

        if agora - ultima_noticia >= timedelta(minutes=30):
            topico = noticia_topicos[indice_topico % len(noticia_topicos)]
            noticias = (buscar_noticias_newsapi(topico) or []) + (buscar_noticias_newsdata(topico) or [])
            msg = nova_noticia(noticias)
            if msg:
                enviar_mensagem(msg)
                if topico == 'criptomoeda':
                    cotacao = buscar_cotacoes()
                    if cotacao:
                        enviar_mensagem(cotacao)
            indice_topico += 1
            ultima_noticia = agora

        if agora - ultima_motivacional >= timedelta(hours=2):
            enviar_motivacional()
            ultima_motivacional = agora

        time.sleep(60)
