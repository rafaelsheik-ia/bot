
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
    "Conheça essa ferramenta incrível de IA para designers: https://www.canva.com/",
    "Curso gratuito de Python com certificado: https://www.cursoemvideo.com/",
    "Como criar uma renda online com afiliados: https://hotmart.com/",
    "Ferramentas para automatizar seu marketing: https://zapier.com/"
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
        print("Mensagem enviada:", mensagem)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

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
            print(f"Erro ao buscar notícias: {e}")
    return noticias

def nova_noticia(lista):
    hoje = datetime.utcnow().date()
    for noticia in lista:
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
            print("Notícia nova:", titulo)
            return f"""🗞 <b>{titulo}</b>\n{url}"""
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
        msg = f"""COTAÇÕES ATUAIS\nBitcoin: ${btc["usd"]:,} | R${btc["brl"]:,}\nEthereum: ${eth["usd"]:,} | R${eth["brl"]:,}\nDólar: R${dolar:.2f} | Euro: R${euro:.2f}"""
        return msg
    except Exception as e:
        print(f"Erro cotação: {e}")
        return None

def buscar_ouro_prata():
    try:
        ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        url = (
            f'https://metals-api.com/api/{ontem}'
            f'?access_key={METALS_API_KEY}&base=USD&symbols=XAU,XAG'
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data.get('success', False):
            print("Erro ao buscar metais:", data.get('error', {}))
            return None
        ouro = data['rates']['XAU']
        prata = data['rates']['XAG']
        ouro_valor = 1 / ouro
        prata_valor = 1 / prata
        msg = (
f"""Metais Preciosos (cotação de {ontem})\n"
f"""Ouro (XAU): ${ouro_valor:.2f} por onça troy\n"
f"""Prata (XAG): ${prata_valor:.2f} por onça troy"""
        )
        return msg
    except Exception as e:
        print(f"Erro ao buscar metais: {e}")
        return None

def enviar_receita(tipo):
    receitas = {
        "cafe": [
            "🥣 <b>Receita Saudável de Café da Manhã</b>
Smoothie de banana com aveia e chia.
👉 https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/",
            "🍞 Panqueca de banana fit sem farinha!
👉 https://www.tudogostoso.com.br/receita/176404-panqueca-de-banana-fit.html"
        ],
        "almoco": [
            "🍛 <b>Almoço Saudável</b>
Frango grelhado com legumes no vapor.
👉 https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/",
            "🥗 Salada completa com grão-de-bico.
👉 https://panelinha.com.br/receita/salada-de-grao-de-bico"
        ],
        "jantar": [
            "🍽 <b>Jantar Leve</b>
Omelete de forno com legumes.
👉 https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html",
            "🥪 Sanduíche natural com frango e cenoura.
👉 https://www.receiteria.com.br/receita/sanduiche-natural-de-frango/"
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
    else:
        mensagem = random.choice(mensagens_boa_noite)
    enviar_mensagem(mensagem)

def enviar_conteudo_digital():
    mensagem = random.choice(conteudos_digitais)
    enviar_mensagem(mensagem)

def iniciar_bot():
    enviado_cafe = False
    enviado_almoco = False
    enviado_jantar = False
    ultima_cotacao = datetime.now() - timedelta(hours=1)
    ultima_noticia = datetime.now() - timedelta(minutes=30)
    ultima_motivacional = datetime.now() - timedelta(hours=2)



if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True, use_reloader=False)).start()
    iniciar_bot()

