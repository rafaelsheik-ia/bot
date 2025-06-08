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
API_TUBE_KEY = 'api_live_TSGaZx9AKt5AVpWi5PWFAJMJPPIhUkCLP5gTfAQHbpiANT4hA4Mxvx'
NEWSDATA_KEY = 'pub_2f53083927874e8bbe43b5a87755a2cd'
METALS_API_KEY = '93d171ec531b8034b1f9d577912de823'

ENVIADAS = set()

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

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Notícias Online"

@app.route('/status')
def status():
    return {"status": "online", "enviadas": len(ENVIADAS)}

def enviar_mensagem(mensagem):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML'}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def buscar_noticias_apitube(topico):
    try:
        hoje = datetime.utcnow().date()
        url = f'https://newsdata.io/api/1/news?apikey={API_TUBE_KEY}&q={topico}&language=pt&from_date={hoje}'
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            return resposta.json().get('results', [])
    except Exception as e:
        print(f"Erro API Tube: {e}")
    return []

def buscar_noticias_newsdata(topico):
    try:
        hoje = datetime.utcnow().date()
        url = f'https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topico}&language=pt&from_date={hoje}'
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            return resposta.json().get('results', [])
    except Exception as e:
        print(f"Erro Newsdata: {e}")
    return []

def nova_noticia(lista):
    hoje = datetime.utcnow().date()
    for noticia in lista:
        data_pub = noticia.get("pubDate") or noticia.get("published_at") or noticia.get("publishedAt")
        url = noticia.get("url") or noticia.get("link")
        titulo = noticia.get("title", "Sem título")

        if data_pub:
            try:
                data_noticia = datetime.strptime(data_pub[:10], "%Y-%m-%d").date()
                if data_noticia != hoje:
                    continue
            except:
                continue

        if url and url not in ENVIADAS:
            ENVIADAS.add(url)
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

def buscar_ouro_prata():
    try:
        url = (
            'https://metals-api.com/api/latest'
            f'?access_key={METALS_API_KEY}&base=USD&symbols=XAU,XAG'
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data.get('success', False):
            print("Erro ao buscar metais:", data.get('error', {}))
            return None
        ouro = data['rates']['XAU']
        prata = data['rates']['XAG']
        msg = (
            f"🥇 <b>Metais Preciosos</b>\n"
            f"💰 Ouro (XAU): ${1 / ouro:.2f} por onça troy\n"
            f"🥈 Prata (XAG): ${1 / prata:.2f} por onça troy"
        )
        return msg
    except Exception as e:
        print(f"Erro ao buscar metais: {e}")
        return None

def enviar_receita(tipo):
    receitas = {
        "cafe": [
            "🥣 <b>Receita Saudável de Café da Manhã</b>\nSmoothie de banana com aveia e chia.\n👉 https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/",
            "🍞 Panqueca de banana fit sem farinha!\n👉 https://www.tudogostoso.com.br/receita/176404-panqueca-de-banana-fit.html"
        ],
        "almoco": [
            "🍛 <b>Almoço Saudável</b>\nFrango grelhado com legumes no vapor.\n👉 https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/",
            "🥗 Salada completa com grão-de-bico.\n👉 https://panelinha.com.br/receita/salada-de-grao-de-bico"
        ],
        "jantar": [
            "🍽 <b>Jantar Leve</b>\nOmelete de forno com legumes.\n👉 https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html",
            "🥪 Sanduíche natural com frango e cenoura.\n👉 https://www.receiteria.com.br/receita/sanduiche-natural-de-frango/"
        ]
    }
    if tipo in receitas:
        mensagem = random.choice(receitas[tipo])
        enviar_mensagem(mensagem)

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
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    ultima_cotacao = datetime.now() - timedelta(hours=1)
    ultima_noticia = datetime.now() - timedelta(minutes=30)
    ultima_motivacional = datetime.now() - timedelta(hours=2)

    enviado_cafe = False
    enviado_almoco = False
    enviado_jantar = False

    noticia_topicos = ['inteligência artificial', 'criptomoeda', 'tecnologia']
    indice_topico = 0

    while True:
        agora = datetime.now()

        if agora.hour == 8 and agora.minute == 0 and not enviado_cafe:
            enviar_receita("cafe")
            enviado_cafe = True
        elif agora.hour == 12 and agora.minute == 0 and not enviado_almoco:
            enviar_receita("almoco")
            enviado_almoco = True
        elif agora.hour == 18 and agora.minute == 0 and not enviado_jantar:
            enviar_receita("jantar")
            enviado_jantar = True
        elif agora.hour == 0 and agora.minute == 0:
            enviado_cafe = enviado_almoco = enviado_jantar = False

        if agora - ultima_cotacao >= timedelta(hours=1):
            cotacao = buscar_cotacoes()
            metais = buscar_ouro_prata()
            if cotacao:
                enviar_mensagem(cotacao)
            if metais:
                enviar_mensagem(metais)
            ultima_cotacao = agora

        if agora - ultima_noticia >= timedelta(minutes=30):
            topico = noticia_topicos[indice_topico % len(noticia_topicos)]
            noticias = (
                buscar_noticias_apitube(topico) +
                buscar_noticias_newsdata(topico)
            )
            msg = nova_noticia(noticias)

            if not msg:
                # Nenhuma notícia relevante foi encontrada, buscar global
                fallback_topico = "notícia mundial"
                noticias_fallback = (
                    buscar_noticias_apitube(fallback_topico) +
                    buscar_noticias_newsdata(fallback_topico)
                )
                msg = nova_noticia(noticias_fallback)
                if msg:
                    msg = "🌍 <b>Notícia Importante do Mundo</b>\n" + msg

            if msg:
                enviar_mensagem(msg)

            indice_topico += 1
            ultima_noticia = agora

        if agora - ultima_motivacional >= timedelta(hours=2):
            enviar_motivacional()
            ultima_motivacional = agora

        time.sleep(60)
