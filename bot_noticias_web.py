import requests
import time
import random
import threading
import os
from datetime import datetime, timedelta
from flask import Flask

# === CONFIGS ===
TELEGRAM_TOKEN = '8067274719:AAEWHOSwqquzP3qvhBKZryM7QfTMEAbMPhg'
CHAT_ID = '-1002562674482'
API_TUBE_KEY = 'api_live_TSGaZx9AKt5AVpWi5PWFAJMJPPIhUkCLP5gTfAQHbpiANT4hA4Mxvx'
NEWSDATA_KEY = 'pub_2f53083927874e8bbe43b5a87755a2cd'
METALS_API_KEY = '93d171ec531b8034b1f9d577912de823'
ENVIADAS = set()

# === FLASK ===
app = Flask(__name__)
@app.route('/')
def home(): return "Bot de Notícias Online"
@app.route('/status')
def status(): return {"status": "online", "enviadas": len(ENVIADAS)}

# === ENVIAR MENSAGEM ===
def enviar_mensagem(mensagem):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML'}
        requests.post(url, data=data, timeout=10)
        print("Mensagem enviada:", mensagem)
    except Exception as e:
        print("Erro ao enviar:", e)

# === MENSAGENS MOTIVACIONAIS ===
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

# === RECEITAS ===
receitas = {
    "cafe": [
        "🥣 <b>Café da Manhã:</b> Smoothie de banana com aveia.\n👉 https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/",
        "🍞 Panqueca de banana fit!\n👉 https://www.tudogostoso.com.br/receita/176404-panqueca-de-banana-fit.html"
    ],
    "almoco": [
        "🍛 <b>Almoço:</b> Frango grelhado com legumes.\n👉 https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/",
        "🥗 Salada com grão-de-bico.\n👉 https://panelinha.com.br/receita/salada-de-grao-de-bico"
    ],
    "jantar": [
        "🍽 <b>Jantar:</b> Omelete de forno com legumes.\n👉 https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html",
        "🥪 Sanduíche natural com frango.\n👉 https://www.receiteria.com.br/receita/sanduiche-natural-de-frango/"
    ]
}

def enviar_receita(tipo):
    if tipo in receitas:
        enviar_mensagem(random.choice(receitas[tipo]))

def enviar_motivacional():
    hora = datetime.now().hour
    if 6 <= hora < 12:
        enviar_mensagem(random.choice(mensagens_bom_dia))
    elif 12 <= hora < 18:
        enviar_mensagem(random.choice(mensagens_boa_tarde))
    else:
        enviar_mensagem(random.choice(mensagens_boa_noite))

# === COTAÇÕES ===
def buscar_cripto_fiat():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl,eur'
        r = requests.get(url, timeout=10).json()
        btc, eth = r['bitcoin'], r['ethereum']
        dolar = btc['usd'] / btc['brl']
        euro = btc['eur'] / btc['brl']
        msg = (
            f"💰 <b>Cripto & Moedas</b>\n"
            f"Bitcoin: ${btc['usd']:,} | R${btc['brl']:,}\n"
            f"Ethereum: ${eth['usd']:,} | R${eth['brl']:,}\n"
            f"Dólar: R${dolar:.2f} | Euro: R${euro:.2f}"
        )
        return msg
    except Exception as e:
        print("Erro cotação:", e)

def buscar_ouro_prata():
    try:
        ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        url = f'https://metals-api.com/api/{ontem}?access_key={METALS_API_KEY}&base=USD&symbols=XAU,XAG'
        r = requests.get(url, timeout=10).json()
        if not r.get('success'): return None
        ouro = 1 / r['rates']['XAU']
        prata = 1 / r['rates']['XAG']
        return f"🪙 <b>Metais Preciosos</b>\nOuro: ${ouro:.2f} | Prata: ${prata:.2f}"
    except Exception as e:
        print("Erro metais:", e)

# === NOTÍCIAS ===
def buscar_noticias(topico):
    noticias = []
    ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    fontes = [
        f'https://newsdata.io/api/1/news?apikey={API_TUBE_KEY}&q={topico}&language=pt&from_date={ontem}',
        f'https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topico}&language=pt&from_date={ontem}'
    ]
    for url in fontes:
        try:
            r = requests.get(url, timeout=10)
            noticias += r.json().get('results', [])
        except: continue
    return noticias

def nova_noticia(lista):
    hoje = datetime.utcnow().date()
    for noticia in lista:
        titulo = noticia.get("title", "Sem título")
        url = noticia.get("url") or noticia.get("link")
        data_pub = noticia.get("pubDate") or noticia.get("published_at")
        try:
            if data_pub and (hoje - datetime.strptime(data_pub[:10], "%Y-%m-%d").date()).days > 1:
                continue
        except: continue
        if url and url not in ENVIADAS:
            ENVIADAS.add(url)
            return f"🗞 <b>{titulo}</b>\n{url}"
    return None

# === LOOP AUTOMÁTICO ===
def loop_automacoes():
    topicos = ["inteligência artificial", "criptomoeda", "tecnologia", "notícia mundial"]
    index_topico = 0
    while True:
        agora = datetime.now()
        
        # Receita por hora
        if agora.hour == 8:
            enviar_receita("cafe")
        elif agora.hour == 12:
            enviar_receita("almoco")
        elif agora.hour == 18:
            enviar_receita("jantar")
        
        # Motivacional em 3 horários
        if agora.hour in [7, 13, 20]:
            enviar_motivacional()

        # Buscar notícia e enviar
        for _ in range(len(topicos)):
            noticias = buscar_noticias(topicos[index_topico])
            msg = nova_noticia(noticias)
            index_topico = (index_topico + 1) % len(topicos)
            if msg:
                enviar_mensagem(msg)
                break

        # Cotação cripto e fiat
        cotacao1 = buscar_cripto_fiat()
        if cotacao1:
            enviar_mensagem(cotacao1)
        time.sleep(10)

        # Cotação de metais
        cotacao2 = buscar_ouro_prata()
        if cotacao2:
            enviar_mensagem(cotacao2)

        time.sleep(1800)  # Espera 30 minutos para repetir

# === INÍCIO ===
if __name__ == '__main__':
    threading.Thread(target=loop_automacoes).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
