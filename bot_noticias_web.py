import requests
import time
import random
import threading
import os
from datetime import datetime, timedelta
from flask import Flask

# === Configurações ===
TELEGRAM_TOKEN = '8067274719:AAEWHOSwqquzP3qvhBKZryM7QfTMEAbMPhg'
CHAT_ID = '-1002562674482'
API_TUBE_KEY = 'api_live_TSGaZx9AKt5AVpWi5PWFAJMJPPIhUkCLP5gTfAQHbpiANT4hA4Mxvx'
NEWSDATA_KEY = 'pub_2f53083927874e8bbe43b5a87755a2cd'
METALS_API_KEY = '93d171ec531b8034b1f9d577912de823'

ENVIADAS = set()
ULTIMO_TEMA = -1

app = Flask(__name__)

mensagens_bom_dia = [
    "Bom dia! Descubra hoje como a IA e o mundo cripto estão mudando o mundo! 👉 https://t.me/rafaelsheikIA",
    "Comece o dia aprendendo algo novo com as maiores inovações! 👉 https://t.me/rafaelsheikIA"
]
mensagens_boa_tarde = [
    "Boa tarde! Mantenha o foco nos seus objetivos com tecnologia e liberdade financeira! 👉 https://t.me/rafaelsheikIA",
    "Que sua tarde seja tão produtiva quanto um algoritmo bem treinado! 👉 https://t.me/rafaelsheikIA"
]
mensagens_boa_noite = [
    "Boa noite! Enquanto o mundo dorme, a inovação não para. Fique por dentro! 👉 https://t.me/rafaelsheikIA",
    "Que sua noite seja tranquila e sua mente cheia de ideias brilhantes! 👉 https://t.me/rafaelsheikIA"
]

receitas = {
    "cafe": [
        "🥣 Receita Saudável de Café da Manhã\nSmoothie de banana com aveia 👉 https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/",
        "🍞 Panqueca de banana fit sem farinha 👉 https://www.tudogostoso.com.br/receita/176404-panqueca-de-banana-fit.html"
    ],
    "almoco": [
        "🍛 Almoço Saudável\nFrango grelhado com legumes 👉 https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/",
        "🥗 Salada completa com grão-de-bico 👉 https://panelinha.com.br/receita/salada-de-grao-de-bico"
    ],
    "jantar": [
        "🍽 Jantar Leve\nOmelete de forno com legumes 👉 https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html",
        "🥪 Sanduíche natural com frango e cenoura 👉 https://www.receiteria.com.br/receita/sanduiche-natural-de-frango/"
    ]
}

temas = ["inteligência artificial", "criptomoeda", "tecnologia", "notícia mundial"]

@app.route('/')
def home():
    return "Bot de Notícias está online!"

def enviar_mensagem(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=data, timeout=10)
        print("Mensagem enviada:", msg)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def buscar_noticias(topico):
    ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    urls = [
        f"https://newsdata.io/api/1/news?apikey={API_TUBE_KEY}&q={topico}&language=pt&from_date={ontem}",
        f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topico}&language=pt&from_date={ontem}"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            for noticia in data.get("results", []):
                link = noticia.get("link") or noticia.get("url")
                if link and link not in ENVIADAS:
                    ENVIADAS.add(link)
                    titulo = noticia.get("title", "Sem título")
                    return f"🗞 <b>{titulo}</b>\n{link}"
        except Exception as e:
            print("Erro ao buscar notícia:", e)
    return None

def buscar_ouro_prata():
    ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        url = f"https://metals-api.com/api/{ontem}?access_key={METALS_API_KEY}&base=USD&symbols=XAU,XAG"
        r = requests.get(url, timeout=10)
        data = r.json()
        ouro = 1 / data['rates']['XAU']
        prata = 1 / data['rates']['XAG']
        return f"💰 Metais Preciosos (ontem {ontem})\nOuro: ${ouro:.2f}/oz\nPrata: ${prata:.2f}/oz"
    except Exception as e:
        print("Erro metais:", e)
        return None

def buscar_cripto():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl,eur'
        r = requests.get(url, timeout=10).json()
        btc, eth = r['bitcoin'], r['ethereum']
        return (
            f"₿ Cotações Cripto\n"
            f"Bitcoin: ${btc['usd']:,} | R${btc['brl']:,}\n"
            f"Ethereum: ${eth['usd']:,} | R${eth['brl']:,}"
        )
    except Exception as e:
        print("Erro cripto:", e)
        return None

def enviar_motivacional():
    hora = datetime.now().hour
    if 6 <= hora < 12:
        msg = random.choice(mensagens_bom_dia)
    elif 12 <= hora < 18:
        msg = random.choice(mensagens_boa_tarde)
    else:
        msg = random.choice(mensagens_boa_noite)
    enviar_mensagem(msg)

def enviar_receita():
    hora = datetime.now().hour
    if 6 <= hora < 12:
        tipo = "cafe"
    elif 12 <= hora < 18:
        tipo = "almoco"
    else:
        tipo = "jantar"
    enviar_mensagem(random.choice(receitas[tipo]))

def ciclo_bot():
    global ULTIMO_TEMA
    while True:
        agora = datetime.now()
        minuto = agora.minute

        # Notícias
        ULTIMO_TEMA = (ULTIMO_TEMA + 1) % len(temas)
        noticia = buscar_noticias(temas[ULTIMO_TEMA])
        if noticia:
            enviar_mensagem(noticia)
        else:
            print("Nenhuma notícia nova.")

        # Cotação alternada
        if minuto % 60 < 30:
            cotacao = buscar_cripto()
        else:
            cotacao = buscar_ouro_prata()
        if cotacao:
            enviar_mensagem(cotacao)

        # Motivacional e receitas em horários certos
        if agora.hour in [7, 12, 18] and agora.minute < 2:
            enviar_receita()
        if agora.hour in [8, 13, 21] and agora.minute < 2:
            enviar_motivacional()

        time.sleep(1800)  # Espera 30 minutos

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False)).start()
    ciclo_bot()
