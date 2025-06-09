import requests
import random
import time
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re
import threading
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
RECEITAS_ENVIADAS = set()  # Para controlar receitas já enviadas
CURSOS_ENVIADOS = set()  # Para controlar cursos já enviados

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

def buscar_noticias_rss():
    """Busca notícias atualizadas do RSS (com fallback para G1)"""
    try:
        # Tenta primeiro a Agência Brasil
        url = 'https://agenciabrasil.ebc.com.br/rss.xml'
        resp = requests.get(url, timeout=15)
        print(f"DEBUG: Resposta RSS Agência Brasil: Status {resp.status_code}")
        
        # Se Agência Brasil falhar, usa G1 como fallback
        if resp.status_code != 200:
            print("DEBUG: Agência Brasil falhou, tentando G1...")
            url = 'https://g1.globo.com/rss/g1/'
            resp = requests.get(url, timeout=15)
            print(f"DEBUG: Resposta RSS G1: Status {resp.status_code}")
        
        if resp.status_code == 200:
            # Parse do XML RSS
            root = ET.fromstring(resp.content)
            
            # Busca pelos itens de notícia
            items = root.findall('.//item')
            
            if not items:
                print("DEBUG: Nenhum item encontrado no RSS")
                return None
            
            # Pega uma notícia aleatória dos primeiros 10 itens (mais recentes)
            recent_items = items[:10]
            item = random.choice(recent_items)
            
            # Extrai informações da notícia
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            
            if title is not None and link is not None:
                title_text = title.text.strip()
                link_text = link.text.strip()
                
                # Verifica se já foi enviada
                if link_text in ENVIADAS:
                    print("DEBUG: Notícia já foi enviada, tentando outra...")
                    return None
                
                ENVIADAS.add(link_text)
                
                # Limpa a descrição removendo HTML
                desc_text = ""
                if description is not None and description.text:
                    desc_text = re.sub(r'<[^>]+>', '', description.text)
                    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                    # Limita o tamanho da descrição
                    if len(desc_text) > 200:
                        desc_text = desc_text[:200] + "..."
                
                fonte = "Agência Brasil" if "agenciabrasil" in url else "G1"
                
                return (
                    f"📰 <b>NOTÍCIA ATUALIZADA</b>\n\n"
                    f"<b>{title_text}</b>\n\n"
                    f"{desc_text}\n\n"
                    f"🔗 <a href='{link_text}'>Leia mais</a>\n"
                    f"📺 Fonte: {fonte}"
                )
            else:
                print("DEBUG: Título ou link não encontrados no item RSS")
                return None
        else:
            print(f"DEBUG: RSS retornou status {resp.status_code}")
            return None
            
    except ET.ParseError as e:
        print(f"DEBUG: Erro ao fazer parse do XML RSS: {e}")
        return None
    except requests.exceptions.Timeout:
        print("DEBUG: Timeout na requisição RSS")
        return "⚠️ Timeout ao buscar notícias."
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Erro de conexão RSS: {e}")
        return "⚠️ Erro de conexão ao buscar notícias."
    except Exception as e:
        print(f"DEBUG: Erro geral ao buscar notícias RSS: {e}")
        return None

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
        # Usando CryptoCompare API (gratuita e sem chave)
        url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD,BRL'
        resp = requests.get(url, timeout=15)
        print(f"DEBUG: Resposta CryptoCompare API: Status {resp.status_code}, Body: {resp.text[:100]}...")
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Verifica se os dados estão completos
            if 'BTC' not in data or 'ETH' not in data:
                print("DEBUG: Dados incompletos da CryptoCompare")
                return None
                
            btc = data['BTC']
            eth = data['ETH']
            
            # Verifica se todas as moedas estão presentes
            if 'BRL' not in btc or 'USD' not in btc or 'BRL' not in eth or 'USD' not in eth:
                print("DEBUG: Moedas faltando nos dados da CryptoCompare")
                return None
            
            return (
                "💰 <b>COTAÇÕES CRYPTO</b>\n"
                f"₿ Bitcoin: R${btc['BRL']:,.0f} | ${btc['USD']:,.0f}\n"
                f"⟠ Ethereum: R${eth['BRL']:,.0f} | ${eth['USD']:,.0f}"
            )
        else:
            print(f"DEBUG: CryptoCompare retornou status {resp.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("DEBUG: Timeout na requisição CryptoCompare")
        return "⚠️ Timeout ao buscar cotações de criptomoedas."
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Erro de conexão CryptoCompare: {e}")
        return "⚠️ Erro de conexão ao buscar cotações de criptomoedas."
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

def buscar_cursos_gratuitos():
    """Busca cursos gratuitos do RSS do FreeCodeCamp"""
    try:
        url = 'https://www.freecodecamp.org/news/rss/'
        resp = requests.get(url, timeout=15)
        print(f"DEBUG: Resposta RSS FreeCodeCamp: Status {resp.status_code}")
        
        if resp.status_code == 200:
            # Parse do XML RSS
            root = ET.fromstring(resp.content)
            
            # Busca pelos itens de artigo/curso
            items = root.findall('.//item')
            
            if not items:
                print("DEBUG: Nenhum item encontrado no RSS do FreeCodeCamp")
                return None
            
            # Filtra artigos relacionados a cursos, tutoriais, etc.
            course_keywords = ['tutorial', 'course', 'learn', 'guide', 'how to', 'beginner', 'introduction', 'complete']
            course_items = []
            
            for item in items[:20]:  # Verifica os 20 mais recentes
                title = item.find('title')
                if title is not None and title.text:
                    title_text = title.text.lower()
                    if any(keyword in title_text for keyword in course_keywords):
                        course_items.append(item)
            
            if not course_items:
                print("DEBUG: Nenhum curso encontrado no RSS")
                return None
            
            # Pega um curso aleatório
            item = random.choice(course_items)
            
            # Extrai informações do curso
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            
            if title is not None and link is not None:
                title_text = title.text.strip()
                link_text = link.text.strip()
                
                # Verifica se já foi enviado
                if link_text in CURSOS_ENVIADOS:
                    print("DEBUG: Curso já foi enviado, tentando outro...")
                    return None
                
                CURSOS_ENVIADOS.add(link_text)
                
                # Limpa a descrição removendo HTML
                desc_text = ""
                if description is not None and description.text:
                    desc_text = re.sub(r'<[^>]+>', '', description.text)
                    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                    # Limita o tamanho da descrição
                    if len(desc_text) > 250:
                        desc_text = desc_text[:250] + "..."
                
                return (
                    f"🎓 <b>CURSO GRATUITO DISPONÍVEL</b>\n\n"
                    f"<b>{title_text}</b>\n\n"
                    f"{desc_text}\n\n"
                    f"🔗 <a href='{link_text}'>Acessar curso gratuito</a>\n\n"
                    f"📚 Fonte: FreeCodeCamp"
                )
            else:
                print("DEBUG: Título ou link não encontrados no item RSS")
                return None
        else:
            print(f"DEBUG: RSS FreeCodeCamp retornou status {resp.status_code}")
            return None
            
    except ET.ParseError as e:
        print(f"DEBUG: Erro ao fazer parse do XML RSS FreeCodeCamp: {e}")
        return None
    except requests.exceptions.Timeout:
        print("DEBUG: Timeout na requisição RSS FreeCodeCamp")
        return "⚠️ Timeout ao buscar cursos."
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Erro de conexão RSS FreeCodeCamp: {e}")
        return "⚠️ Erro de conexão ao buscar cursos."
    except Exception as e:
        print(f"DEBUG: Erro geral ao buscar cursos RSS: {e}")
        return None

def buscar_receita_nova():
    """Busca uma receita nova da API gratuita de receitas"""
    try:
        url = 'https://api-receitas-pi.vercel.app/receitas/todas'
        resp = requests.get(url, timeout=10)
        print(f"DEBUG: Resposta API Receitas: Status {resp.status_code}, Body: {resp.text[:100]}...")
        
        if resp.status_code == 200:
            receitas = resp.json()
            
            # Filtra receitas que ainda não foram enviadas
            receitas_disponiveis = [r for r in receitas if r['id'] not in RECEITAS_ENVIADAS]
            
            # Se todas as receitas já foram enviadas, limpa o histórico e reinicia
            if not receitas_disponiveis:
                print("DEBUG: Todas as receitas foram enviadas, reiniciando lista...")
                RECEITAS_ENVIADAS.clear()
                receitas_disponiveis = receitas
            
            if receitas_disponiveis:
                receita = random.choice(receitas_disponiveis)
                RECEITAS_ENVIADAS.add(receita['id'])
                
                # Formata a receita para envio
                nome = receita['receita']
                ingredientes = receita['ingredientes']
                modo_preparo = receita['modo_preparo']
                tipo = receita.get('tipo', 'receita')
                
                # Limita o tamanho para não exceder limite do Telegram
                if len(ingredientes) > 200:
                    ingredientes = ingredientes[:200] + "..."
                if len(modo_preparo) > 300:
                    modo_preparo = modo_preparo[:300] + "..."
                
                return (
                    f"🍽️ <b>Receita: {nome}</b>\n\n"
                    f"📝 <b>Ingredientes:</b>\n{ingredientes}\n\n"
                    f"👨‍🍳 <b>Modo de Preparo:</b>\n{modo_preparo}\n\n"
                    f"🏷️ Tipo: {tipo.title()}"
                )
            else:
                return None
        else:
            print(f"DEBUG: API Receitas retornou status {resp.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro ao buscar receita nova: {e}")
        return None

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

def enviar_curso_do_dia():
    """Envia cursos gratuitos em horários específicos"""
    hora = datetime.now().hour
    
    # Envia cursos em horários específicos (diferentes das receitas)
    if hora in [10, 14, 20]:  # 10h, 14h e 20h
        curso = buscar_cursos_gratuitos()
        if curso:
            enviar_mensagem(curso)
        else:
            print("DEBUG: Nenhum curso novo encontrado no momento")

def enviar_receita_do_dia():
    global ULTIMA_RECEITA
    hora = datetime.now().hour
    hoje = datetime.now().date()
    if ULTIMA_RECEITA == (hora, hoje):
        return

    # Envia receita em horários específicos
    if hora in [8, 12, 18, 22]:
        receita = buscar_receita_nova()
        if receita:
            enviar_mensagem(receita)
            ULTIMA_RECEITA = (hora, hoje)
        else:
            enviar_mensagem("⚠️ Não foi possível buscar uma receita nova no momento.")

def enviar_inicio():
    """Função chamada uma única vez no início."""
    print("🚀 Enviando mensagens iniciais...")

    enviar_mensagem("🤖 Bot iniciado! Aqui está sua primeira dose de informação:")

    # Motivacional e Receita (independente da hora, só no início)
    enviar_mensagem("💡 Motivação: " + random.choice(mensagens_motivacionais["bom_dia"])) 
    
    # Busca uma receita nova da API
    receita_nova = buscar_receita_nova()
    if receita_nova:
        enviar_mensagem(receita_nova)
    else:
        enviar_mensagem("⚠️ Não foi possível buscar uma receita no momento.") 

    # Curso gratuito (só no início)
    curso_inicial = buscar_cursos_gratuitos()
    if curso_inicial:
        enviar_mensagem(curso_inicial)
    else:
        enviar_mensagem("⚠️ Nenhum curso disponível no momento.")

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

        # Notícias atualizadas (prioriza RSS da Agência Brasil)
        noticia_rss = buscar_noticias_rss()
        if noticia_rss:
            enviar_mensagem(noticia_rss)
        else:
            # Fallback para a API antiga se RSS falhar
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

        # Mensagens motivacionais, receitas e cursos (com lógica de horário dentro das funções)
        enviar_motivacional()
        enviar_receita_do_dia()
        enviar_curso_do_dia()  # Nova função de cursos

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


