import streamlit as st
import yfinance as yf
import google.generativeai as genai
from duckduckgo_search import DDGS
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Bibliotecas de Análise Técnica
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volume import OnBalanceVolumeIndicator

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv()
st.set_page_config(page_title="Gemini Whale Hunter", page_icon="🐋", layout="wide")

# --- GERENCIAMENTO DE ESTADO ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def ir_para_analise():
    st.session_state.page = 'analise'

def voltar_home():
    st.session_state.page = 'home'

# --- FUNÇÕES DE DADOS ---
def configure_genai():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
        else:
            st.error("❌ Erro: Chave de API não encontrada.")
            return None
    genai.configure(api_key=api_key)
    return True

def get_data():
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(period="6mo")
    if df.empty: return None
    df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
    df["EMA_20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
    df["EMA_50"] = EMAIndicator(close=df["Close"], window=50).ema_indicator()
    df["OBV"] = OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"]).on_balance_volume()
    return df

def get_news():
    results = []
    try:
        with DDGS() as ddgs:
            query_br = "Bitcoin mercado financeiro economia eua fed taxa juros brasil criptomoedas"
            news_br = ddgs.text(query_br, region='br-br', timelimit='d', max_results=4)
            if news_br:
                for r in news_br:
                    title = r.get('title', 'Sem titulo')
                    link = r.get('href', '')
                    results.append(f"- {title} (Fonte: {link})")
            else:
                return "Sem notícias relevantes."
        return "\n".join(results)
    except Exception as e:
        return f"Erro na busca: {e}"

def get_ai_analysis(df, news_text):
    if df is None: return "Erro nos dados."
    last = df.iloc[-1]
    prev = df.iloc[-2]
    obv_trend = "SUBINDO (Dinheiro Entrando 🟢)" if last['OBV'] > prev['OBV'] else "CAINDO (Dinheiro Saindo 🔴)"
    price_trend = "ALTA" if last['EMA_20'] > last['EMA_50'] else "BAIXA"
    
    prompt = f"""
    Aja como um Analista Sênior de Investimentos.
    
    DADOS TÉCNICOS BTC: Preço ${last['Close']:.2f} | RSI {last['RSI']:.2f} | Tendência {price_trend} | Baleias (OBV) {obv_trend}
    MANCHETES DO MERCADO: {news_text}
    
    TAREFA: Crie uma análise dividida em 3 partes curtas (Use Markdown):
    
    1. 🐳 **O QUE AS BALEIAS E GRÁFICOS DIZEM:**
       Analise o RSI e o OBV. É hora de compra ou venda?
       
    2. 🌍 **CENÁRIO MACRO ECONÔMICO (IMPORTANTE):**
       Analise as notícias sobre Economia (Fed, Juros, Dólar) e diga como isso impacta o Bitcoin hoje.
       
    3. 🔮 **VEREDITO FINAL (3 DIAS):**
       O preço deve Subir, Cair ou Lateralizar? Dê uma previsão clara.
       
    IMPORTANTE: Use negrito nas partes chaves.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

# --- PÁGINA 1: HOME ---
def show_home():
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-image: url("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2832&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .big-title {
            font-size: 5rem !important;
            font-weight: 900 !important;
            text-align: center !important;
            color: #ffffff !important;
            text-shadow: 0 0 20px #00d2ff;
            margin-top: 50px;
        }
        .subtitle {
            font-size: 1.5rem !important;
            text-align: center !important;
            color: #e2e8f0 !important;
            text-shadow: 2px 2px 4px #000000;
        }
        div.stButton > button {
            background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
            color: black;
            font-size: 24px;
            font-weight: 900;
            border-radius: 50px;
            padding: 15px 40px;
            border: 3px solid white;
            box-shadow: 0px 0px 20px rgba(255, 65, 108, 0.5);
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            color: white;
            border-color: black;
        }
        .crypto-bar { display: flex; justify-content: center; gap: 20px; margin-top: 30px; flex-wrap: wrap; }
        .crypto-icon { width: 60px; height: 60px; filter: drop-shadow(0 0 5px rgba(255,255,255,0.5)); }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="big-title">🐋 GEMINI CRYPTO HUNTER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Inteligência Artificial rastreando Baleias, Preço e Macroeconomia em Tempo Real</p>', unsafe_allow_html=True)
    
    logos_html = """
    <div class="crypto-bar">
        <img src="https://cryptologos.cc/logos/bitcoin-btc-logo.png" class="crypto-icon">
        <img src="https://cryptologos.cc/logos/ethereum-eth-logo.png" class="crypto-icon">
        <img src="https://cryptologos.cc/logos/solana-sol-logo.png" class="crypto-icon">
        <img src="https://cryptologos.cc/logos/bnb-bnb-logo.png" class="crypto-icon">
        <img src="https://cryptologos.cc/logos/xrp-xrp-logo.png" class="crypto-icon">
        <img src="https://cryptologos.cc/logos/tether-usdt-logo.png" class="crypto-icon">
    </div>
    """
    st.markdown(logos_html, unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.button("🚀 RASTREAR BALEIAS E ANALISAR MERCADOS", on_click=ir_para_analise, use_container_width=True)

# --- PÁGINA 2: ANÁLISE ---
def show_analysis():
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-image: none !important;
            background-color: #0e1117 !important;
        }
        /* CORREÇÃO DE CORES (Tudo Branco e Negrito) */
        
        /* 1. Títulos das Métricas (RSI, Tendência, etc) */
        div[data-testid="stMetricLabel"] p {
            color: #ffffff !important;
            font-weight: 900 !important; /* Negrito */
            font-size: 1.1rem !important;
        }
        div[data-testid="stMetricLabel"] {
             color: #ffffff !important; /* Fallback */
        }
        
        /* 2. Valores das Métricas (Os números) */
        div[data-testid="stMetricValue"] {
            color: #00d2ff !important; /* Azul Neon para o número */
            font-weight: 900 !important;
        }

        /* 3. Texto da IA */
        .ai-box, .ai-box p, .ai-box div, .ai-box span, .ai-box li {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 18px !important;
            line-height: 1.6 !important;
        }
        .ai-box strong {
            color: #00d2ff !important;
            font-weight: 900 !important;
        }
        .ai-box {
            background-color: rgba(20, 25, 40, 0.9);
            border: 2px solid #00d2ff;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.15);
            margin-top: 20px;
        }

        h1, h2, h3 { color: #ffffff !important; }
        
        .affiliate-btn {
            display: block;
            width: 100%;
            padding: 15px;
            background-color: #FCD535; 
            color: black !important;
            text-align: center;
            text-decoration: none;
            font-weight: 900;
            font-size: 18px;
            border-radius: 10px;
            margin-bottom: 10px;
            transition: 0.3s;
        }
        .affiliate-btn:hover { opacity: 0.9; transform: scale(1.01); }
        .ledger-btn { background-color: #1C1C1C; color: white !important; border: 2px solid white; }
    </style>
    """, unsafe_allow_html=True)

    st.button("⬅️ Voltar para Capa", on_click=voltar_home)

    if configure_genai():
        with st.spinner("🤖 Lendo gráficos, notícias do Fed e dados on-chain..."):
            df = get_data()
            if df is not None:
                news = get_news()
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                st.markdown("## 📊 Painel de Controle das Baleias")
                
                # Métricas
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Preço BTC", f"${latest['Close']:,.2f}")
                c2.metric("RSI (Força)", f"{latest['RSI']:.0f}")
                c3.metric("Tendência", "Alta 🐂" if latest['EMA_20'] > latest['EMA_50'] else "Baixa 🐻")
                obv_diff = latest['OBV'] - prev['OBV']
                c4.metric("Fluxo Baleias", "Entrando 🟢" if obv_diff > 0 else "Saindo 🔴", delta=f"{obv_diff:,.0f}")

                # Gráfico (Correção das Legendas para Branco)
                st.markdown("---")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Preço", line=dict(color='#fbbf24', width=3)))
                fig.add_trace(go.Scatter(x=df.index, y=df['OBV'], name="Volume Baleias", line=dict(color='#00d2ff', width=2), yaxis='y2', fill='tozeroy'))
                
                fig.update_layout(
                    height=500, 
                    title=dict(text="Preço vs. Acumulação das Baleias (6 Meses)", font=dict(color="white", size=20)), # Título Branco
                    template="plotly_dark",
                    yaxis2=dict(overlaying='y', side='right'), 
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend=dict(font=dict(color="white", size=14, family="Arial Black")), # LEGENDA BRANCA E GROSSA
                    font=dict(color="white") # Tudo branco no gráfico
                )
                st.plotly_chart(fig, use_container_width=True)

                # ÁREA DE LUCRO
                st.markdown("---")
                col_mon1, col_mon2 = st.columns(2)
                with col_mon1:
                    st.markdown('<a href="https://accounts.binance.com/register" target="_blank" class="affiliate-btn">🟡 Abrir conta na Binance (Seguro)</a>', unsafe_allow_html=True)
                with col_mon2:
                    st.markdown('<a href="https://shop.ledger.com/" target="_blank" class="affiliate-btn ledger-btn">🔒 Proteger Moedas com Ledger</a>', unsafe_allow_html=True)
                
                # ÁREA DA IA
                st.markdown("### 🧠 Análise Completa do Gemini")
                analise_texto = get_ai_analysis(df, news)
                st.markdown(f"""
                <div class="ai-box">
                    {analise_texto.replace(chr(10), '<br>')} 
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error("Erro ao carregar dados.")

# --- CONTROLADOR ---
if st.session_state.page == 'home':
    show_home()
elif st.session_state.page == 'analise':
    show_analysis()
