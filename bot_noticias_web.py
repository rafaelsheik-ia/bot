import requests, time, random, threading, os
from datetime import datetime, timedelta
from flask import Flask

# —————————————————————
TELEGRAM_TOKEN = '8067274719:AAEWHOSwqquzP3qvhBKZryM7QfTMEAbMPhg'
CHAT_ID          = '-1002562674482'
API_TUBE_KEY     = 'api_live_TSGaZx9AKt5AVpWi5PWFAJMJPPIhUkCLP5gTfAQHbpiANT4hA4Mxvx'
NEWSDATA_KEY     = 'pub_2f53083927874e8bbe43b5a87755a2cd'
METALS_API_KEY   = '93d171ec531b8034b1f9d577912de823'
ENVIADAS = set()
temas = ["inteligência artificial","criptomoeda","tecnologia","notícia mundial"]
# —————————————————————

app = Flask(__name__)
@app.route('/')
def home(): return "Bot de Notícias Online"
@app.route('/status')
def status(): return {"status": "online", "enviadas": len(ENVIADAS)}

def enviar_mensagem(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id':CHAT_ID,'text':msg,'parse_mode':'HTML'}, timeout=10)
        print("✅ Enviado:", msg.split("\n")[0])
    except Exception as e:
        print("❌ Erro envio:", e)

# —————————————————————

def buscar_noticias(topico):
    ontem = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    noticias = []
    for key in [API_TUBE_KEY, NEWSDATA_KEY]:
        try:
            r = requests.get(f"https://newsdata.io/api/1/news?apikey={key}&q={topico}&language=pt&from_date={ontem}", timeout=10).json()
            noticias += r.get("results", [])
        except:
            continue
    return noticias

def nova_noticia(lista):
    today = datetime.utcnow().date()
    for n in lista:
        if not isinstance(n, dict): continue
        title = n.get("title", "Sem título")
        url   = n.get("url") or n.get("link")
        pub   = n.get("pubDate") or n.get("published_at") or ""
        try:
            date_n = datetime.strptime(pub[:10], "%Y-%m-%d").date()
            if (today - date_n).days > 1: continue
        except:
            pass
        if url and url not in ENVIADAS:
            ENVIADAS.add(url)
            return f"🗞 <b>{title}</b>\n{url}"
    return None

# —————————————————————

def cotacao_cripto_fiat():
    try:
        j = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,brl,eur", timeout=10).json()
        btc, eth = j['bitcoin'], j['ethereum']
        d = btc['usd']/btc['brl']; e = btc['eur']/btc['brl']
        return (f"💰 Cripto & Moedas:\n"
                f"BTC: ${btc['usd']:,} | R${btc['brl']:,}\n"
                f"ETH: ${eth['usd']:,} | R${eth['brl']:,}\n"
                f"Dólar: R${d:.2f} | Euro: R${e:.2f}")
    except Exception as e:
        print("❌ Erro cripto:", e)

def cotacao_ouro_prata():
    try:
        oh = (datetime.utcnow()-timedelta(days=1)).strftime("%Y-%m-%d")
        r = requests.get(f"https://metals-api.com/api/{oh}?access_key={METALS_API_KEY}&base=USD&symbols=XAU,XAG", timeout=10).json()
        if not r.get("success"): return None
        o = 1 / r['rates']['XAU']; p = 1/ r['rates']['XAG']
        return f"🪙 Metais ({oh}):\nOuro: ${o:.2f}/oz\nPrata: ${p:.2f}/oz"
    except Exception as e:
        print("❌ Erro metais:", e)

# —————————————————————

# Saudação e receitas
def saudacao_motivacional():
    h = datetime.now().hour
    msgs = {
        'bom dia': ["Bom dia! Inove sua manhã.", "Que sua manhã seja brilhante!"],
        'boa tarde': ["Boa tarde! Continue conectado.", "Tarde produtiva à vista!"],
        'boa noite': ["Boa noite! Hora de relaxar.", "Noite de descanso e criatividade!"]
    }
    if 6<=h<12: return random.choice(msgs['bom dia'])
    if 12<=h<18: return random.choice(msgs['boa tarde'])
    return random.choice(msgs['boa noite'])

def receita_diaria():
    h = datetime.now().hour
    rcs = {
        8: "Receita: Smoothie de banana com aveia! 🍌",
        12:"Receita: Frango grelhado com legumes! 🍛",
        18:"Receita: Omelete de forno com legumes! 🍳"
    }
    return rcs.get(h)

# —————————————————————

def loop_automacoes():
    print("🔁 Loop iniciado…")
    top_idx = 0
    while True:
        now = datetime.now()
        # Envio inicial imediato
        # 1) notícia
        msg = nova_noticia(buscar_noticias(temas[top_idx]))
        if msg:
            enviar_mensagem(msg)
        top_idx = (top_idx+1) % len(temas)
        # 2) cotação cripto/fiat
        cc = cotacao_cripto_fiat()
        if cc: enviar_mensagem(cc)
        # 3) cotação ouro/prata
        mp = cotacao_ouro_prata()
        if mp: enviar_mensagem(mp)
        # saudação e receitas
        sa = saudacao_motivacional(); rx = receita_diaria()
        if sa: enviar_mensagem(sa)
        if rx: enviar_mensagem(rx)

        # aguarda 30 minutos
        for _ in range(30):
            time.sleep(60)
            # dentro deste tempo, envia motivacional ou receita se bater o horário
            sa = saudacao_motivacional(); rx = receita_diaria()
            if sa: enviar_mensagem(sa)
            if rx: enviar_mensagem(rx)

# —————————————————————

if __name__ == "__main__":
    threading.Thread(target=loop_automacoes, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
