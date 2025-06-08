import requests
import time
import threading
import random
from datetime import datetime, timedelta
from flask import Flask

# === CHAVES FIXADAS ===
TELEGRAM_TOKEN = '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ1234567890'
CHAT_ID = '-1001234567890'
API_TUBE_KEY = 'api_live_TSGaZx9AKt5AVpWi5PWFAJMJPPIhUkCLP5gTfAQHbpiANT4hA4Mxvx'
NEWSDATA_KEY = 'pub_2f53083927874e8bbe43b5a87755a2cd'
METALS_API_KEY = '93d171ec531b8034b1f9d577912de823'

# === VARIÁVEIS DE CONTROLE ===
ENVIADAS = set()
ULTIMA_MOTIVACIONAL = (-1, None)
ULTIMA_RECEITA = (-1, None)

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
        resp = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl')
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
    "bom_dia": ["🌞 Bom dia! Comece aprendendo algo novo 👉 https://t.me/rafaelsheikIA"],
    "boa_tarde": ["🌤 Boa tarde! Mantenha o foco 👉 https://t.me/rafaelsheikIA"],
    "boa_noite": ["🌙 Boa noite! Enquanto o mundo dorme, a inovação não para 👉 https://t.me/rafaelsheikIA"]
}

receitas = {
    "cafe": ["☕ Smoothie com aveia: https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/"],
    "almoco": ["🍛 Frango com legumes: https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/"],
    "jantar": ["🍲 Omelete de forno: https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html"]
}

def enviar_motivacional():
    global ULTIMA_MOTIVACIONAL
    hora = datetime.now().hour
    hoje = datetime.now().date()

    if ULTIMA_MOTIVACIONAL == (hora, hoje):
        return

    tipo = None
    if hora == 8:
        tipo = "bom_dia"
    elif hora == 12:
        tipo = "boa_tarde"
    elif hora == 18:
        tipo = "boa_noite"

    if tipo:
        mensagem = random.choice(mensagens_motivacionais[tipo])
        enviar_mensagem(mensagem)
        ULTIMA_MOTIVACIONAL = (hora, hoje)

def enviar_receita_do_dia():
    global ULTIMA_RECEITA
    hora = datetime.now().hour
    hoje = datetime.now().date()

    if ULTIMA_RECEITA == (hora, hoje):
        return

    tipo = None
    if hora == 8:
        tipo = "cafe"
    elif hora == 12:
        tipo = "almoco"
    elif hora == 18:
        tipo = "jantar"

    if tipo:
        mensagem = random.choice(receitas[tipo])
        enviar_mensagem(mensagem)
        ULTIMA_RECEITA = (hora, hoje)

def loop_automacoes():
    topicos = ["inteligência artificial", "criptomoeda", "tecnologia", "notícia mundial"]

    # 🔥 Enviar algo logo ao iniciar (força uma mensagem ao vivo)
    enviar_mensagem("🤖 Bot de notícias iniciado e operando!")
    
    msg = buscar_noticias("inteligência artificial") or buscar_noticias("criptomoeda")
    if msg:
        enviar_mensagem(msg)
    else:
        enviar_mensagem("⚠️ Nenhuma notícia disponível agora.")

    cot = buscar_cotacoes()
    if cot:
        enviar_mensagem(cot)

    metais = buscar_metais()
    if metais:
        enviar_mensagem(metais)

    # 🔁 Entra no loop normal após o envio inicial
    while True:
        print("🔄 Executando automações...")

        enviar_motivacional()
        enviar_receita_do_dia()

        random.shuffle(topicos)
        for topico in topicos:
            msg = buscar_noticias(topico)
            if msg:
                enviar_mensagem(msg)
                break

        cot = buscar_cotacoes()
        if cot:
            enviar_mensagem(cot)

        time.sleep(60)

        metais = buscar_metais()
        if metais:
            enviar_mensagem(metais)

        time.sleep(1740)


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)).start()
    threading.Thread(target=loop_automacoes).start()
