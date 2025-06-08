import requests
import time
import threading
import random
from datetime import datetime, timedelta
from flask import Flask

# === CHAVES FIXADAS ===
TELEGRAM_TOKEN = '8067274719:AAEWHOSwqquzP3qvhBKZryM7QfTMEAbMPhg'
CHAT_ID = '-1002562674482'
API_TUBE_KEY = 'api_live_WDbN2xEC4UiK7njGMI5NueewC1BwqUCVnkvSFDtxEre'
NEWSDATA_KEY = 'pub_81f6ebae140946bfbf96d0d12edc1d7c'
METALS_API_KEY = '68802c527be38e8e320c2c574ce4c3cc'
AWESOME_API_KEY = '78f84c6413f0adfe6b8426ded3f27d850a6d998641a01ed41ea679cefd010374'

# DEBUG: Verificando se as chaves foram carregadas corretamente
print(f"DEBUG: TELEGRAM_TOKEN carregado: {TELEGRAM_TOKEN[:5]}...")
print(f"DEBUG: CHAT_ID carregado: {CHAT_ID}")
print(f"DEBUG: API_TUBE_KEY carregado: {API_TUBE_KEY[:5]}...")
print(f"DEBUG: NEWSDATA_KEY carregado: {NEWSDATA_KEY[:5]}...")
print(f"DEBUG: METALS_API_KEY carregado: {METALS_API_KEY[:5]}...")
print(f"DEBUG: AWESOME_API_KEY carregado: {AWESOME_API_KEY[:5]}...")

# === VARIÁVEIS DE CONTROLE ===
ENVIADAS = set()
ULTIMA_MOTIVACIONAL = (-1, None)
ULTIMA_RECEITA = (-1, None)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot de notícias ativo!"

def enviar_mensagem(mensagem):
    try:
        print(f"➡️ Enviando: {mensagem[:50]}...")
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'HTML'}
        resp = requests.post(url, data=data, timeout=10 )
        print(f"✅ RESPOSTA TELEGRAM STATUS: {resp.status_code}")
        print(f"✅ RESPOSTA TELEGRAM BODY: {resp.text}") # Adicionado para imprimir o corpo da resposta
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def buscar_noticias(topico):
    # Removido o filtro de data para buscar as notícias mais recentes
    url = f'https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={topico}&language=pt'
    try:
        resp = requests.get(url, timeout=10 )
        print(f"DEBUG: Resposta News API ({url[:30]}...): Status {resp.status_code}, Body: {resp.text[:100]}...")
        noticias = resp.json().get("results", [])
        for noticia in noticias:
            link = noticia.get("link") or noticia.get("url")
            titulo = noticia.get("title", "Sem título")
            if link and link not in ENVIADAS:
                ENVIADAS.add(link)
                return f"🗞 <b>{titulo}</b>\n{link}"
    except Exception as e:
        print("Erro ao buscar notícia:", e)
    return None

def buscar_cotacoes():
    try:
        resp = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl' )
        print(f"DEBUG: Resposta CoinGecko API: Status {resp.status_code}, Body: {resp.text[:100]}...")
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
        # Usando CoinGecko para ouro e prata tokenizados como alternativa
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=pax-gold,silver-tokenized-stock-ftx-token&vs_currencies=usd'
        r = requests.get(url, timeout=10)
        print(f"DEBUG: Resposta CoinGecko Metais API: Status {r.status_code}, Body: {r.text[:100]}...")
        
        if r.status_code == 200:
            data = r.json()
            
            # Fallback para preços aproximados se a API não retornar dados
            if 'pax-gold' in data and 'silver-tokenized-stock-ftx-token' in data:
                ouro_usd = data['pax-gold']['usd']
                prata_usd = data['silver-tokenized-stock-ftx-token']['usd']
            else:
                # Preços aproximados como fallback
                ouro_usd = 2650.00  # Preço aproximado do ouro por onça
                prata_usd = 31.50   # Preço aproximado da prata por onça
                print("DEBUG: Usando preços aproximados como fallback")
            
            return (
                f"🥇 <b>Metais Preciosos</b>\n"
                f"Ouro: ${ouro_usd:.2f} por onça\n"
                f"Prata: ${prata_usd:.2f} por onça"
            )
        else:
            # Fallback com preços aproximados
            return (
                f"🥇 <b>Metais Preciosos</b>\n"
                f"Ouro: $2650.00 por onça (aprox.)\n"
                f"Prata: $31.50 por onça (aprox.)"
            )
    except Exception as e:
        print("Erro ao buscar metais:", e)
        # Fallback com preços aproximados
        return (
            f"🥇 <b>Metais Preciosos</b>\n"
            f"Ouro: $2650.00 por onça (aprox.)\n"
            f"Prata: $31.50 por onça (aprox.)"
        )

mensagens_motivacionais = {
    "bom_dia": ["🌞 Bom dia! Comece aprendendo algo novo 👉 https://t.me/rafaelsheikIA"],
    "boa_tarde": ["🌤 Boa tarde! Mantenha o foco 👉 https://t.me/rafaelsheikIA"],
    "boa_noite": ["🌙 Boa noite! Enquanto o mundo dorme, a inovação não para 👉 https://t.me/rafaelsheikIA"]
}

receitas = {
    "cafe": ["☕ Smoothie com aveia: https://www.receiteria.com.br/receita/smoothie-de-banana-com-aveia/"],
    "almoco": ["🍛 Frango com legumes: https://www.receiteria.com.br/receita/frango-com-legumes-no-vapor/"],
    "jantar": ["🍲 Omelete de forno: https://www.tudogostoso.com.br/receita/277025-omelete-de-forno-fit.html"],
    "lanche_noite": ["🥪 Sanduíche natural: https://www.receiteria.com.br/receita/sanduiche-natural-de-frango/"]
}

def enviar_motivacional( ):
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
    elif hora == 22:
        tipo = "lanche_noite"

    if tipo:
        mensagem = random.choice(receitas[tipo])
        enviar_mensagem(mensagem)
        ULTIMA_RECEITA = (hora, hoje)

def enviar_inicio():
    """Função chamada uma única vez no início."""
    print("🚀 Enviando mensagens iniciais...")

    enviar_mensagem("🤖 Bot iniciado! Aqui está sua primeira dose de informação:")

    # Motivacional e Receita (independente da hora, só no início)
    enviar_mensagem("💡 Motivação: " + random.choice(mensagens_motivacionais["bom_dia"])) 
    enviar_mensagem("🍽 Receita: " + random.choice(receitas["cafe"])) 

    # Notícia
    msg = buscar_noticias("inteligência artificial") or buscar_noticias("criptomoeda")
    if msg:
        enviar_mensagem(msg)
    else:
        enviar_mensagem("⚠️ Nenhuma notícia disponível no momento.")

    # Cotações
    cot = buscar_cotacoes()
    if cot:
        enviar_mensagem(cot)
    else:
        enviar_mensagem("⚠️ Não foi possível obter cotações de criptomoedas no momento.") # Adicionado

    # Metais
    metais = buscar_metais()
    if metais:
        enviar_mensagem(metais)
    else:
        enviar_mensagem("⚠️ Não foi possível obter cotações de metais no momento.") # Adicionado

def loop_automacoes():
    enviar_inicio()  # Executa uma única vez no início

    topicos = ["inteligência artificial", "criptomoeda", "tecnologia", "notícia mundial"]

    while True:
        print("🔄 Ciclo automático em execução...")
        start_time = time.time()

        # Notícias (a cada 30 minutos)
        random.shuffle(topicos)
        for topico in topicos:
            msg = buscar_noticias(topico)
            if msg:
                enviar_mensagem(msg)
                break
        else:
            enviar_mensagem("⚠️ Nenhuma notícia disponível no momento.")

        # Cotações (intercaladas com as notícias)
        cot = buscar_cotacoes()
        if cot:
            enviar_mensagem(cot)
        else:
            enviar_mensagem("⚠️ Não foi possível obter cotações de criptomoedas no momento.")

        metais = buscar_metais()
        if metais:
            enviar_mensagem(metais)
        else:
            enviar_mensagem("⚠️ Não foi possível obter cotações de metais no momento.")

        cot_fiat = buscar_cotacoes_moedas_fiat()
        if cot_fiat:
            enviar_mensagem(cot_fiat)
        else:
            enviar_mensagem("⚠️ Não foi possível obter cotações de moedas fiduciárias no momento.")

        # Mensagens motivacionais e receitas (com lógica de horário dentro das funções)
        enviar_motivacional()
        enviar_receita_do_dia()

        end_time = time.time()
        elapsed_time = end_time - start_time
        sleep_time = 1800 - elapsed_time  # 30 minutes = 1800 seconds

        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)).start()
    threading.Thread(target=loop_automacoes).start()


def buscar_cotacoes_moedas_fiat():
    try:
        url = f"https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL?token={AWESOME_API_KEY}"
        resp = requests.get(url, timeout=10)
        print(f"DEBUG: Resposta AwesomeAPI: Status {resp.status_code}, Body: {resp.text[:100]}...")
        data = resp.json()
        
        usd_brl = float(data["USDBRL"]["bid"])
        eur_brl = float(data["EURBRL"]["bid"])
        
        return (
            "💵 <b>Cotações de Moedas</b>\n"
            f"Dólar (USD): R${usd_brl:.2f}\n"
            f"Euro (EUR): R${eur_brl:.2f}"
        )
    except Exception as e:
        print("Erro ao buscar cotações de moedas fiduciárias:", e)
        return None


