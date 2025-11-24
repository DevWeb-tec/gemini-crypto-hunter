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

# --- CSS (ESTILO VISUAL) ---
st.markdown("""
<style>
    /* 1. Imagem de Fundo */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2832&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* 2. Fundo Transparente para Leitura */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(5px);
        padding: 2rem !important;
        border-radius: 20px;
        max-width: 1400px;
    }

    /* 3. Título GIGANTE */
    .big-title {
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        color: #ffffff !important;
        text-transform: uppercase;
        text-shadow: 0 0 20px #00d2ff;
        margin-bottom: 0px !important;
    }
    
    /* 4. Legenda */
    .subtitle {
        font-size: 1.5rem !important;
        text-align: center !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        margin-bottom: 30px !important;
        text-shadow: 2px 2px 4px #000000;
    }

    /* 5. Ícones */
    .crypto-bar {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 40px;
        flex-wrap: wrap;
    }
    .crypto-icon {
        width: 60px;
        height: 60px;
        transition: transform 0.2s;
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
    }
    .crypto-icon:hover {
        transform: scale(1.2);
    }

    /* 6. ESTILO DO BOTÃO (Texto Grosso e Visível) */
    div.stButton > button {
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%) !important;
        
        /* TEXTO PRETO E GROSSO */
        color: #000000 !important; 
        font-size: 26px !important; /* Letra Maior */
        font-weight: 900 !important; /* Ultra Negrito */
        text-transform: uppercase !important;
        text-shadow: 0px 1px 0px rgba(255,255,255,0.4) !important; /* Borda leve para destacar */
        
        border: 3px solid rgba(255,255,255,0.8) !important; /* Borda branca grossa */
        border-radius: 50px !important;
        padding: 15px 30px !important;
        box-shadow: 0px 0px 30px rgba(255, 65, 108, 0.6) !important;
        transition: all 0.3s ease !important;
        width: 100%;
        height: auto;
        white-space: normal !important; /* Permite que o texto quebre se precisar */
    }
    
    div.stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0px 0px 50px rgba(255, 65, 108, 1) !important;
        color: #ffffff !important; /* Vira branco no hover */
        border-color: #000000 !important;
    }

    /* Métricas */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        color: white !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<h1 class="big-title">🐋 GEMINI CRYPTO HUNTER</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Inteligência Artificial rastreando Baleias, Preço e Notícias em Tempo Real</p>', unsafe_allow_html=True)

# --- ÍCONES ---
logos_html = """
<div class="crypto-bar">
    <img src="https://cryptologos.cc/logos/bitcoin-btc-logo.png" class="crypto-icon">
    <img src="https://cryptologos.cc/logos/ethereum-eth-logo.png" class="crypto-icon">
    <img src="https://cryptologos.cc/logos/solana-sol-logo.png" class="crypto-icon">
    <img src="https://cryptologos.cc/logos/bnb-bnb-logo.png" class="crypto-icon">
    <img src="https://cryptologos.cc/logos/xrp-xrp-logo.png" class="crypto-icon">
    <img src="https://cryptologos.cc/logos/dogecoin-doge-logo.png" class="crypto-icon">
    <img src="https://cryptologos.cc/logos/tether-usdt-logo.png" class="crypto-icon">
</div>
"""
st.markdown(logos_html, unsafe_allow_html=True)

# --- FUNÇÕES ---
def configure_genai():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ Erro: Chave de API não encontrada no .env")
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
            query_br = "Bitcoin análise tendência infomoney cointelegraph brasil investnews"
            news_br = ddgs.text(query_br, region='br-br', timelimit='d', max_results=3)
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
    Aja como um Analista On-Chain Profissional.
    DADOS BTC/USD: Preço ${last['Close']:.2f} | RSI {last['RSI']:.2f} | Tendência {price_trend} | Baleias (OBV) {obv_trend}
    NOTÍCIAS: {news_text}
    TAREFA: Análise curta e direta sobre o preço e as baleias para os próximos 3 dias.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

# --- INTERFACE ---
if configure_genai():
    
    # --- AJUSTE DE COLUNAS PARA DEIXAR O BOTÃO MAIS ESTREITO ---
    # Usando [3, 2, 3] significa: 
    # Esquerda: 37.5% da tela (Vazio)
    # Meio:     25% da tela (Botão) -> Fica bem mais estreito!
    # Direita:  37.5% da tela (Vazio)
    col_left, col_center, col_right = st.columns([3, 2, 3])
    
    with col_center:
        analyze_click = st.button("🚀 RASTREAR BALEIAS E ANALISAR MERCADOS", use_container_width=True)

    if analyze_click:
        with st.spinner("🛰️ Analisando dados on-chain..."):
            try:
                df = get_data()
                if df is not None:
                    news = get_news()
                    latest = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    st.markdown("---")
                    
                    # Métricas
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Preço", f"${latest['Close']:,.2f}")
                    c2.metric("RSI", f"{latest['RSI']:.0f}")
                    c3.metric("Tendência", "Alta 🐂" if latest['EMA_20'] > latest['EMA_50'] else "Baixa 🐻")
                    obv_diff = latest['OBV'] - prev['OBV']
                    c4.metric("Baleias (OBV)", "Entrando" if obv_diff > 0 else "Saindo", delta=f"{obv_diff:,.0f}")

                    # Gráfico
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Preço", line=dict(color='#fbbf24', width=3)))
                    fig.add_trace(go.Scatter(x=df.index, y=df['OBV'], name="Baleias", line=dict(color='#00d2ff', width=2), yaxis='y2', fill='tozeroy'))
                    fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                      yaxis2=dict(overlaying='y', side='right'), 
                                      font=dict(color='white'))
                    st.plotly_chart(fig, use_container_width=True)

                    # IA
                    st.info(get_ai_analysis(df, news))
                    
            except Exception as e:
                st.error(f"Erro: {e}")