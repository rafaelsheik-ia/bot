import requests
import time
import random
import threading
import os
from datetime import datetime, timedelta
from flask import Flask

TELEGRAM_TOKEN = '8067274719:AAEWHOSwqquzP3qvhBKZryM7QfTMEAbMPhg'
CHAT_ID = '-1002562674482'
API_TUBE_KEY = 'api_live_TSGaZx9AKt5AVpWi5PWFAJMJPPIhUkCLP5gTfAQHbpiANT4hA4Mxvx'
NEWSDATA_KEY = 'pub_2f53083927874e8bbe43b5a87755a2cd'
METALS_API_KEY = '93d171ec531b8034b1f9d577912de823'

ENVIADAS = set()

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

conteudos_digitais = [
    "Ferramenta incrível de IA para designers: https://www.canva.com/",
    "Curso gratuito de Python com certificado: https://www.cursoemvideo.com/",
    "Como criar uma renda online com afiliados: https://hotmart.com/",
    "Ferramentas para automatizar seu marketing: https://zapier.com/"
]

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Notícias Online"

def enviar_mensagem(mensagem):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML'}
        requests.post(url, data=data, timeout=10)
        print("✅ Mensagem enviada:", mensagem)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def buscar_noticias(topico):
    noticias = []
    hoje = datetime.utcnow().date()
    ontem = hoje - timedelta(days=1)
    urls = [
        f'https://newsdata.io/api/1/news?apikey={API_TUBE_KEY}&q={topico}&language=pt&from_date={ontem}',
        f'https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topico}&language=pt&from_date={ontem}'
    ]
    for url in urls:
        try:
            resposta = requests.get(url, timeout=10)
            if resposta.status_code == 200:
                noticias += resposta.json().get('results', [])
        except Exception as e:
            print("❌ Erro ao buscar notícias:", e)
    return noticias

def nova_noticia(lista):
    hoje = datetime.utcnow().date()
    for noticia in lista:
        if isinstance(noticia, dict):
            data_pub = noticia.get("pubDate") or noticia.get("published_at") or noticia.get("publishedAt")
            url = noticia.get("url") or noticia.get("link")
            titulo = noticia.get("title", "Sem título")
            if data_pub:
                try:
                    data_noticia = datetime.strptime(data_pub[:10], "%Y-%m-%d").date()
                    if (hoje - data_noticia).days > 1:
                        continue
                except:
                    continue
            if url and url not in ENVIADAS:
                ENVIADAS.add(url)
                return f"🗞 <b>{titulo}</b>\n{url}"
    return None

def buscar_cotacoes():
    try:
        print("🔄 Buscando cotação de cripto/moedas...")
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl,eur'
        r = requests.get(url, timeout=10)
        data = r.json()
        btc = data['bitcoin']
        eth = data['ethereum']
        dolar = btc['usd'] / btc['brl']
        euro = btc['eur'] / btc['brl']
        return f"💱 COTAÇÕES\nBitcoin: ${btc['usd']:,} | R${btc['brl']:,}\nEthereum: ${eth['usd']:,} | R${eth['brl']:,}\nDólar: R${dolar:.2f} | Euro: R${euro:.2f}"
    except Exception as e:
        print("❌ Erro cotação cripto:", e)
        return None

def buscar_ouro_prata():
    try:
        print("🔄 Buscando cotação de metais...")
        ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        url = f'https://metals-api.com/api/{ontem}?access_key={METALS_API_KEY}&base=USD&symbols=XAU,XAG'
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data.get('success', False):
            print("❌ Erro resposta metais:", data.get('error'))
            return None
        ouro = data['rates']['XAU']
        prata = data['rates']['XAG']
        ouro_valor = 1 / ouro
        prata_valor = 1 / prata
        return f"🏅 Metais Preciosos (ontem)\nOuro: ${ouro_valor:.2f} por onça\nPrata: ${prata_valor:.2f} por onça"
    except Exception as e:
        print("❌ Erro metais:", e)
        return None

def enviar_receita(tipo):
    receitas = {
        "cafe": [
            "☕ Receita de café da manhã: Smoothie de banana 👉 https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/",
            "🥞 Panqueca de banana fit 👉 https://www.tudogostoso.com.br/receita/176404-panqueca-de-banana-fit.html"
        ],
        "almoco": [
            "🍽️ Receita de almoço: Frango com legumes 👉 https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/",
            "🥗 Salada com grão-de-bico 👉 https://panelinha.com.br/receita/salada-de-grao-de-bico"
        ],
        "jantar": [
            "🌙 Receita de jantar: Omelete de forno 👉 https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html",
            "🥪 Sanduíche natural 👉 https://www.receiteria.com.br/receita/sanduiche-natural-de-frango/"
        ]
    }
    if tipo in receitas:
        enviar_mensagem(random.choice(receitas[tipo]))

def enviar_motivacional():
    hora = datetime.now().hour
    if 6 <= hora < 12:
        msg = random.choice(mensagens_bom_dia)
    elif 12 <= hora < 18:
        msg = random.choice(mensagens_boa_tarde)
    else:
        msg = random.choice(mensagens_boa_noite)
    enviar_mensagem(msg)

def loop_automacoes():
    enviado_cafe = False
    enviado_almoco = False
    enviado_jantar = False
    while True:
        agora = datetime.now()
        hora = agora.hour

        # Motivacional a cada 2h
        if agora.minute == 0 and hora % 2 == 0:
            print("🕒 Enviando mensagem motivacional")
            enviar_motivacional()

        # Receita de acordo com hora
        if hora == 8 and not enviado_cafe:
            print("🥣 Enviando café da manhã")
            enviar_receita("cafe")
            enviado_cafe = True
        elif hora == 12 and not enviado_almoco:
            print("🍽️ Enviando almoço")
            enviar_receita("almoco")
            enviado_almoco = True
        elif hora == 18 and not enviado_jantar:
            print("🌙 Enviando jantar")
            enviar_receita("jantar")
            enviado_jantar = True

        if hora == 0:
            enviado_cafe = enviado_almoco = enviado_jantar = False

        # Notícias a cada 30 min
        if agora.minute % 30 == 0:
            for topico in ["IA", "Crypto", "Tecnologia", "Notícia Mundial"]:
                print(f"📰 Buscando notícias sobre {topico}")
                noticias = buscar_noticias(topico)
                msg = nova_noticia(noticias)
                if msg:
                    enviar_mensagem(msg)
                    break

        # Cotação
        cotacao1 = buscar_cotacoes()
        if cotacao1:
            enviar_mensagem(cotacao1)
        cotacao2 = buscar_ouro_prata()
        if cotacao2:
            enviar_mensagem(cotacao2)

        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=loop_automacoes).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
