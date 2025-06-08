import requests
import time
import threading
import random
import os
from datetime import datetime, timedelta
from flask import Flask

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
API_TUBE_KEY = os.getenv('API_TUBE_KEY')
NEWSDATA_KEY = os.getenv('NEWSDATA_KEY')
METALS_API_KEY = os.getenv('METALS_API_KEY')

ENVIADAS = set()

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot de notícias ativo!'

def enviar_mensagem(mensagem):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML'}
        requests.post(url, data=data, timeout=10)
        print("✅ Mensagem enviada:", mensagem)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def buscar_noticias(topico):
    ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    urls = [
        f'https://newsdata.io/api/1/news?apikey={API_TUBE_KEY}&q={topico}&language=pt&from_date={ontem}',
        f'https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topico}&language=pt&from_date={ontem}'
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            noticias = resp.json().get('results', [])
            for noticia in noticias:
                link = noticia.get('link') or noticia.get('url')
                titulo = noticia.get('title', 'Sem título')
                if link and link not in ENVIADAS:
                    ENVIADAS.add(link)
                    return f"🗞 <b>{titulo}</b>\n{link}"
        except Exception as e:
            print("Erro ao buscar notícia:", e)
    return None

def buscar_cotacoes():
    try:
        resp = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl,eur')
        data = resp.json()
        btc = data['bitcoin']
        eth = data['ethereum']
        return (
            "💰 <b>COTAÇÕES</b>\n"
            f"Bitcoin: R${btc['brl']:,} | ${btc['usd']:,}\n"
            f"Ethereum: R${eth['brl']:,} | ${eth['usd']:,}"
        )
    except Exception as e:
        print("Erro ao buscar cotações:", e)
        return None

def buscar_metais():
    try:
        ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        url = f'https://metals-api.com/api/{ontem}?access_key={METALS_API_KEY}&base=USD&symbols=XAU,XAG'
        r = requests.get(url)
        data = r.json()
        ouro = data['rates']['XAU']
        prata = data['rates']['XAG']
        return (
            f"🥇 <b>Metais Preciosos ({ontem})</b>\n"
            f"Ouro (XAU): ${1 / ouro:.2f} por onça\n"
            f"Prata (XAG): ${1 / prata:.2f} por onça"
        )
    except Exception as e:
        print("Erro ao buscar metais:", e)
        return None

mensagens_motivacionais = {
    "bom_dia": [
        "🌞 Bom dia! Comece aprendendo algo novo 👉 https://t.me/rafaelsheikIA"
    ],
    "boa_tarde": [
        "🌤 Boa tarde! Mantenha o foco 👉 https://t.me/rafaelsheikIA"
    ],
    "boa_noite": [
        "🌙 Boa noite! Enquanto o mundo dorme, a inovação não para 👉 https://t.me/rafaelsheikIA"
    ]
}

receitas = {
    "cafe": [
        "☕ Smoothie com aveia: https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/"
    ],
    "almoco": [
        "🍛 Frango com legumes: https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/"
    ],
    "jantar": [
        "🍲 Omelete de forno: https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html"
    ]
}

def enviar_motivacional():
    hora = datetime.now().hour
    if hora == 8:
        tipo = "bom_dia"
    elif hora == 12:
        tipo = "boa_tarde"
    elif hora == 18:
        tipo = "boa_noite"
    else:
        return
    mensagem = random.choice(mensagens_motivacionais[tipo])
    enviar_mensagem(mensagem)

def enviar_receita_do_dia():
    hora = datetime.now().hour
    if hora == 8:
        tipo = "cafe"
    elif hora == 12:
        tipo = "almoco"
    elif hora == 18:
        tipo = "jantar"
    else:
        return
    mensagem = random.choice(receitas[tipo])
    enviar_mensagem(mensagem)

def loop_automacoes():
    topicos = ["inteligência artificial", "criptomoeda", "tecnologia", "notícia mundial"]
    while True:
        print("🔄 Executando automações...")

        # Mensagens do dia
        enviar_motivacional()
        enviar_receita_do_dia()

        # Buscar notícia
        for topico in topicos:
            msg = buscar_noticias(topico)
            if msg:
                enviar_mensagem(msg)
                break

        # Cotação cripto/moedas
        cot = buscar_cotacoes()
        if cot:
            enviar_mensagem(cot)

        # Espera 1 min e envia metais
        time.sleep(60)
        metais = buscar_metais()
        if metais:
            enviar_mensagem(metais)

        # Aguarda 30 minutos para repetir o ciclo
        time.sleep(1800)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False, use_reloader=False)).start()
    threading.Thread(target=loop_automacoes).start()
