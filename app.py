import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from textblob import TextBlob
import requests
import xml.etree.ElementTree as ET
import time
import streamlit.components.v1 as components
import re
import json

# --- Configuration ---
st.set_page_config(
    page_title="ProStock | AI-Powered Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .stApp { background-color: #ffffff; color: #333333; }
    
    /* Logo Styles */
    .prostock-logo-sidebar { font-size: 32px; font-weight: 900; color: #0d6efd; margin-bottom: 5px; text-align: center; }
    .prostock-logo-sidebar span { color: #333; }
    
    .homepage-logo { font-size: 60px; font-weight: 900; color: #0d6efd; text-align: center; margin-bottom: 10px; }
    .homepage-logo span { color: #333; }
    
    /* Homepage Elements */
    .hero-container { padding: 20px 20px; text-align: center; }
    
    /* Trending Cards */
    .trend-card {
        background: white; border: 1px solid #f0f0f0; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); transition: all 0.3s ease; height: 100%;
    }
    .trend-card:hover { box-shadow: 0 8px 20px rgba(13, 110, 253, 0.1); transform: translateY(-3px); border-color: #0d6efd; }
    .trend-header { font-size: 16px; color: #333; font-weight: 800; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #f8f9fa; padding-bottom: 10px; }
    .trend-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f8f9fa; font-size: 14px; }
    .trend-item:last-child { border-bottom: none; }
    .trend-name { font-weight: 600; color: #555; }
    .trend-price-badge { font-weight: 700; padding: 4px 8px; border-radius: 6px; font-size: 12px; }
    
    /* Account Top Right */
    .account-bar { display: flex; justify-content: flex-end; align-items: center; gap: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px; }
    .user-badge { font-weight: 600; color: #555; background: #e9ecef; padding: 5px 10px; border-radius: 20px; font-size: 12px; }
    
    /* Header & Logo Integration */
    .finance-header { background-color: #ffffff; border-bottom: 2px solid #f0f0f0; padding-bottom: 20px; margin-bottom: 20px; margin-top: 10px; }
    .asset-logo-img { height: 50px; width: 50px; border-radius: 50%; object-fit: contain; margin-right: 15px; border: 1px solid #eee; background: white; vertical-align: middle; }
    
    /* Stats Grid */
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 15px; margin-top: 15px; }
    .stat-item { font-size: 14px; }
    .stat-label { color: #888; font-size: 12px; }
    .stat-value { font-weight: 600; color: #333; }
    
    /* News Feed (Clean Text Style - No Images) */
    .news-card-row {
        display: flex;
        flex-direction: column; /* Stack vertically for text only */
        background: white;
        border-bottom: 1px solid #eee;
        padding: 15px;
        text-decoration: none;
        transition: background-color 0.2s;
        border-left: 3px solid transparent;
    }
    .news-card-row:hover { background-color: #fcfcfc; border-left: 3px solid #0d6efd; }
    .news-title { font-size: 15px; font-weight: 600; color: #1a0dab; line-height: 1.4; margin-bottom: 5px; text-decoration: none; display: block;}
    .news-meta { font-size: 12px; color: #666; }
    
    /* Gemini Sidebar */
    .gemini-box {
        background-color: #f8f9fa;
        border-left: 1px solid #eee;
        padding: 20px;
        height: 100%;
        min-height: 600px;
    }
    .gemini-header {
        font-size: 20px; font-weight: 700; color: #333; margin-bottom: 20px;
        display: flex; align-items: center; gap: 10px;
    }
    .gemini-logo-icon { width: 30px; height: 30px; }
    
    .chat-bubble {
        background: white; padding: 10px; border-radius: 8px; margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-size: 13px;
        border: 1px solid #eee;
    }
    
    /* Loading */
    .loading-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; animation: fadein 1s; }
    
    /* Layout Fixes */
    .block-container { padding-top: 5rem; max-width: 98%; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- Mock DB & State ---
@st.cache_resource
def get_database(): return {}
db = get_database()

if 'user_id' not in st.session_state: st.session_state['user_id'] = None
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'splash_shown' not in st.session_state: st.session_state['splash_shown'] = False
if 'mode' not in st.session_state: st.session_state['mode'] = "Home" 
if 'ticker_search' not in st.session_state: st.session_state['ticker_search'] = ""
if 'lang' not in st.session_state: st.session_state['lang'] = "English"
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []
if 'gemini_api_key' not in st.session_state: 
    # Set default API Key provided by user
    st.session_state['gemini_api_key'] = "AIzaSyB-RYuBGcCseCvU0a5EXlR8aB1V7KvzDeU"

# --- TRANSLATION DICTIONARY ---
TRANS = {
    "English": {
        "Home": "🏠 Home", "Terminal": "📈 Asset Terminal", "Favs": "⭐ Favorites", "Media": "📺 Media & News", "Map": "🗺️ Finviz Map",
        "Stocks": "Stocks", "Commodities": "Commodities", "Crypto": "Crypto", "Forex": "Currencies/Forex",
        "Search": "Search Assets", "Search_Ph": "Symbol or Name (e.g. Nvidia, Gold, BTC)...", "Trend_Stocks": "🔥 Trending Stocks",
        "Trend_Crypto": "🪙 Top Crypto", "Trend_Fx": "💱 Key Currencies", "Quick": "Quick Access",
        "Chart": "Chart", "AI": "AI Analysis", "News": "News", "Data": "Data", "Fund": "Fundamentals",
        "Convert": "Convert", "Rate_Err": "Rate Unavailable", "Forecast": "30-Period Forecast",
        "Sent": "Market Sentiment", "News_Sent": "News Tone", "Logout": "Log Out", "Delete": "Delete Account",
        "Hero_Sub": "Market Intelligence for the Modern Investor", "Watchlist": "⭐ Watchlist", "Media_Center": "📺 Media Center",
        "Tab_Chart": "Chart", "Tab_AI": "AI Analysis", "Tab_News": "News", "Tab_Data": "Data", "Tab_Fund": "Fundamentals",
        "Trend_KR": "🇰🇷 Korea Markets"
    },
    "한국어": {
        "Home": "🏠 홈", "Terminal": "📈 자산 터미널", "Favs": "⭐ 관심종목", "Media": "📺 미디어 & 뉴스", "Map": "🗺️ 핀비즈 맵",
        "Stocks": "주식", "Commodities": "원자재", "Crypto": "암호화폐", "Forex": "통화/외환",
        "Search": "자산 검색", "Search_Ph": "심볼 또는 이름 (예: 삼성전자, 비트코인)...", "Trend_Stocks": "🔥 인기 주식",
        "Trend_Crypto": "🪙 주요 암호화폐", "Trend_Fx": "💱 주요 통화", "Quick": "빠른 접속",
        "Chart": "차트", "AI": "AI 분석", "News": "뉴스", "Data": "데이터", "Fund": "기업 정보",
        "Convert": "변환", "Rate_Err": "환율 정보 없음", "Forecast": "30일 예측",
        "Sent": "시장 심리", "News_Sent": "뉴스 분위기", "Logout": "로그아웃", "Delete": "계정 삭제",
        "Hero_Sub": "현대 투자자를 위한 시장 인텔리전스", "Watchlist": "⭐ 관심종목", "Media_Center": "📺 미디어 센터",
        "Tab_Chart": "차트", "Tab_AI": "AI 분석", "Tab_News": "뉴스", "Tab_Data": "데이터", "Tab_Fund": "기업 정보",
        "Trend_KR": "🇰🇷 한국 증시"
    }
}

def txt(key):
    return TRANS[st.session_state['lang']].get(key, key)

# --- Loading Screen ---
if not st.session_state['splash_shown']:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""<div class="loading-container"><h1 style='font-size: 50px; font-weight:900; color: #0d6efd;'>Pro<span style="color:#333;">Stock</span></h1><p style='color: #666; margin-bottom: 10px;'>Institutional Grade Analytics</p><p style='color: #0d6efd; font-size: 18px; font-weight: 500;'>professional personal banking</p></div>""", unsafe_allow_html=True)
    time.sleep(3)
    placeholder.empty()
    st.session_state['splash_shown'] = True

# --- Auth ---
def login_user(uid):
    if uid in db:
        st.session_state['user_id'] = uid; st.session_state['logged_in'] = True; st.rerun()
    else: st.error("ID not found")
def signup_user(uid):
    if uid in db: st.error("ID exists")
    else: db[uid]={'favorites':[]}; st.session_state['user_id']=uid; st.session_state['logged_in']=True; st.rerun()
def logout_user():
    st.session_state['user_id']=None; st.session_state['logged_in']=False; st.rerun()
def delete_account():
    if st.session_state['user_id'] in db: del db[st.session_state['user_id']]; logout_user()

# --- LOGIN SCREEN ---
if not st.session_state['logged_in']:
    st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    [data-testid="stHeader"] { background-color: #000000 !important; }
    .login-box { background-color: #111111; padding: 40px; border-radius: 12px; border: 1px solid #222; border-top: 3px solid #0d6efd; box-shadow: 0 0 30px rgba(13, 110, 253, 0.15); text-align: center; margin-top: 50px; }
    .login-title { color: #ffffff; font-family: 'Roboto', sans-serif; font-weight: 900; font-size: 36px; margin-bottom: 5px; }
    .login-subtitle { color: #666; font-size: 14px; margin-bottom: 30px; letter-spacing: 1px; text-transform: uppercase; }
    [data-testid="stTextInput"] input { background-color: #1a1a1a !important; color: #ffffff !important; border: 1px solid #333 !important; }
    [data-testid="stTextInput"] input:focus { border-color: #0d6efd !important; box-shadow: 0 0 0 1px #0d6efd !important; }
    [data-testid="stTextInput"] label { color: #888 !important; }
    .stButton > button { background-color: #000000 !important; color: #0d6efd !important; border: 2px solid #0d6efd !important; border-radius: 8px !important; font-weight: bold !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { background-color: #0d6efd !important; color: #000000 !important; box-shadow: 0 0 15px rgba(13, 110, 253, 0.6) !important; }
    </style>
    """, unsafe_allow_html=True)
    
    c1,c2,c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("""<div class="login-box"><div class="login-title">Pro<span style="color:#0d6efd;">Stock</span></div><p class="login-subtitle">Professional Personal Banking</p></div>""", unsafe_allow_html=True)
        uid = st.text_input("User ID", max_chars=6, type="password", placeholder="Access Code (6 Digits)")
        b1,b2=st.columns(2)
        with b1: 
            if st.button("Log In", type="primary", use_container_width=True): 
                if len(uid)==6 and uid.isdigit(): login_user(uid)
        with b2:
            if st.button("Sign Up", use_container_width=True):
                if len(uid)==6 and uid.isdigit(): signup_user(uid)
    st.stop()

# --- ASSET MAP ---
ASSET_MAP = {
    "BITCOIN": "BTC-USD", "BTC": "BTC-USD", "ETHEREUM": "ETH-USD", "ETH": "ETH-USD",
    "SOLANA": "SOL-USD", "XRP": "XRP-USD", "GOLD": "GC=F", "SILVER": "SI=F",
    "OIL": "CL=F", "USD/KRW": "KRW=X", "APPLE": "AAPL", "TESLA": "TSLA",
    "NVIDIA": "NVDA", "GOOGLE": "GOOGL", "AMAZON": "AMZN", "SAMSUNG": "005930.KS", "DISNEY": "DIS",
    "KOSPI": "^KS11", "KOSDAQ": "^KQ11",
    "비트코인": "BTC-USD", "이더리움": "ETH-USD", "리플": "XRP-USD", "솔라나": "SOL-USD", 
    "삼성전자": "005930.KS", "삼성": "005930.KS", "애플": "AAPL", "테슬라": "TSLA", "엔비디아": "NVDA",
    "금": "GC=F", "원유": "CL=F", "환율": "KRW=X", "원달러": "KRW=X", "코스피": "^KS11", "코스닥": "^KQ11"
}

@st.cache_data(ttl=10)
def get_live_price(ticker):
    try:
        info = yf.Ticker(ticker).info
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price:
            d = yf.Ticker(ticker).history(period="1d")
            if not d.empty: price = d['Close'].iloc[-1]
        prev = info.get('previousClose')
        if not prev:
            d = yf.Ticker(ticker).history(period="5d")
            if len(d) > 1: prev = d['Close'].iloc[-2]
        change = ((price - prev)/prev)*100 if price and prev else 0.0
        return price or 0.0, change
    except: return 0.0, 0.0

@st.cache_data(ttl=10)
def get_stock_data(ticker, interval, period, start=None, end=None):
    try:
        if interval in ['1m', '5m', '1h'] and period == '1d': period = "5d"
        if interval == "1d" and end: end = end + timedelta(days=1)
        if interval == "1d": data = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
        else: data = yf.download(ticker, period=period, interval=interval, progress=False)
        if (data.empty or len(data)<2) and period=="1d":
            data = yf.download(ticker, period="5d", interval=interval, progress=False)
        if 'Volume' in data.columns: data = data[data['Volume']>0]
        data = data.dropna()
        return data
    except: return pd.DataFrame()

@st.cache_data(ttl=300)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info, stock.news
    except: return {}, []

@st.cache_data(ttl=300)
def get_exchange_rate(pair="KRW=X"):
    try:
        data = yf.Ticker(pair).history(period="1d")
        if not data.empty: return data['Close'].iloc[-1]
    except: return None
    return None

def calculate_technicals(data):
    if len(data) < 2: return data
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['SMA'] = data['Close'].rolling(20).mean()
    data['BB_Upper'] = data['SMA'] + 2*data['Close'].rolling(20).std()
    data['BB_Lower'] = data['SMA'] - 2*data['Close'].rolling(20).std()
    return data

def get_fear_and_greed_proxy():
    try:
        vix = yf.Ticker("^VIX").history(period="5d")['Close'].iloc[-1]
        sp500 = yf.Ticker("^GSPC").history(period="6mo")
        if sp500.empty: return 50, "Neutral"
        current_sp = sp500['Close'].iloc[-1]
        avg_sp = sp500['Close'].mean()
        fear_score = max(0, min(100, 100 - (vix - 10) * 2.5))
        momentum_score = max(0, min(100, 50 + ((current_sp - avg_sp) / avg_sp) * 500))
        final_score = (fear_score * 0.4) + (momentum_score * 0.6)
        if final_score < 25: label = "Extreme Fear"; 
        elif final_score < 45: label = "Fear"
        elif final_score < 55: label = "Neutral"
        elif final_score < 75: label = "Greed"
        else: label = "Extreme Greed"
        return int(final_score), label
    except: return 50, "Neutral"

def safe_extract_news_title(item):
    if not isinstance(item, dict): return None
    if 'title' in item and item['title']: return item['title']
    if 'content' in item and isinstance(item['content'], dict):
        if 'title' in item['content'] and item['content']['title']: return item['content']['title']
    for key, value in item.items():
        if isinstance(value, dict):
            res = safe_extract_news_title(value)
            if res: return res
    return None

def analyze_news_sentiment(news_items):
    if not news_items: return 0, 0, 0, "Neutral"
    polarities = []
    for item in news_items:
        title = safe_extract_news_title(item)
        if title:
            blob = TextBlob(title)
            polarities.append(blob.sentiment.polarity)
    if not polarities: return 0, 0, 0, "Neutral"
    pos = sum(1 for p in polarities if p > 0.05)
    neg = sum(1 for p in polarities if p < -0.05)
    neu = len(polarities) - pos - neg
    avg_pol = np.mean(polarities)
    if avg_pol > 0.05: label = "Positive"
    elif avg_pol < -0.05: label = "Negative"
    else: label = "Neutral"
    return pos, neg, neu, label

def generate_ai_report(ticker, price, sma, rsi, fg_score, fg_label, news_label):
    report = f"### 🧠 AI Executive Summary for {ticker}\n\n"
    report += f"**1. Market Sentiment:** {fg_label} ({fg_score}/100).\n"
    report += f"**2. News Analysis:** {news_label} sentiment detected.\n"
    trend = "Bullish 🟢" if price > sma else "Bearish 🔴"
    rsi_state = "Overbought ⚠️" if rsi > 70 else "Oversold 🛒" if rsi < 30 else "Neutral ⚖️"
    report += f"**3. Technicals:** {trend} trend, RSI is {rsi_state}."
    return report

@st.cache_data(ttl=600)
def fetch_rss_feed(url):
    try:
        response = requests.get(url, timeout=5)
        content = response.text
        items = []
        raw_items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        for raw in raw_items[:5]: 
            title_m = re.search(r'<title>(.*?)</title>', raw, re.DOTALL)
            link_m = re.search(r'<link>(.*?)</link>', raw, re.DOTALL)
            if title_m and link_m:
                t = title_m.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
                l = link_m.group(1).strip()
                items.append({'title': t, 'link': l})
        return items
    except: return []

# --- REAL GEMINI AI ---
def call_gemini_api(prompt, api_key):
    # Use Flash Latest as requested
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=" + api_key
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 300}
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        elif r.status_code == 404:
             # Fallback to standard flash if latest alias is missing in region
             url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key
             r = requests.post(url, headers=headers, json=payload)
             if r.status_code == 200:
                return r.json()['candidates'][0]['content']['parts'][0]['text']
        return f"Error: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Connection Error: {e}"

def get_smart_response(query, ticker, data, api_key):
    if not api_key:
        return "⚠️ API Key missing. Please check settings."

    # Check for data availability
    latest_price = data['Close'].iloc[-1] if not data.empty else "N/A"
    rsi_val = f"{data['RSI'].iloc[-1]:.2f}" if 'RSI' in data.columns and not pd.isna(data['RSI'].iloc[-1]) else "N/A"
    sma_val = f"{data['SMA'].iloc[-1]:.2f}" if 'SMA' in data.columns and not pd.isna(data['SMA'].iloc[-1]) else "N/A"

    prompt = f"""
    You are a professional financial analyst. Analyze {ticker} based on this real-time data:
    - Price: {latest_price}
    - RSI (14): {rsi_val}
    - SMA (20): {sma_val}
    
    User Question: "{query}"
    
    Provide a concise, actionable answer (max 3 sentences).
    """
    return call_gemini_api(prompt, api_key)

def submit_chat():
    if st.session_state.chat_input_val:
        user_input = st.session_state.chat_input_val
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        ticker = st.session_state.get('ticker_search', 'Unknown')
        try: 
            d = yf.download(ticker, period="1mo", interval="1d", progress=False)
            d = calculate_technicals(d)
        except: d = pd.DataFrame({'Close': [0]})
        
        api_key = st.session_state.get('gemini_api_key', '')
        
        with st.spinner("AI Thinking..."):
            response = get_smart_response(user_input, ticker, d, api_key)
            st.session_state.chat_history.append({"role": "ai", "content": response})
        
        st.session_state.chat_input_val = "" 

# --- NAVIGATION ---
st.sidebar.markdown('<div class="prostock-logo-sidebar">Pro<span>Stock</span></div>', unsafe_allow_html=True)
if st.sidebar.button(txt("Home"), type="secondary", use_container_width=True): st.session_state['mode'] = "Home"
if st.sidebar.button("🌐 Language: " + st.session_state['lang']):
    st.session_state['lang'] = "한국어" if st.session_state['lang'] == "English" else "English"
    st.rerun()
st.sidebar.markdown("---")
if st.sidebar.button(txt("Terminal"), use_container_width=True): st.session_state['mode'] = "Asset Terminal"
if st.sidebar.button(txt("Favs"), use_container_width=True): st.session_state['mode'] = "Favorites"
if st.sidebar.button(txt("Media"), use_container_width=True): st.session_state['mode'] = "Media & News"
if st.sidebar.button(txt("Map"), use_container_width=True): st.session_state['mode'] = "Map"
mode = st.session_state['mode']
st.sidebar.markdown("---")
with st.sidebar.expander("🧮 Currency Calc", expanded=False):
    cc_amt = st.number_input("Amt", 100.0)
    c1, c2 = st.columns(2)
    with c1: cc_f = st.selectbox("From", ["USD", "KRW", "EUR", "JPY", "BTC"])
    with c2: cc_to = st.selectbox("To", ["KRW", "USD", "EUR", "JPY", "BTC"])
    if st.button(txt("Convert")):
        try:
            if cc_f==cc_to: res=cc_amt
            elif cc_f=='USD': r = yf.Ticker(f"{cc_to}=X").history(period='1d')['Close'].iloc[-1]; res = cc_amt * r if cc_to!='KRW' else cc_amt * r 
            else: res = None 
            if res: st.success(f"{res:,.2f} {cc_to}")
        except: st.error(txt("Rate_Err"))

# --- MODE: HOMEPAGE ---
if mode == "Home":
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    c_fill, c_acc = st.columns([3, 1])
    with c_acc:
        with st.expander(f"👤 ID: {st.session_state['user_id']}"):
            if st.button(txt("Logout"), use_container_width=True): logout_user()
            if st.button(txt("Delete"), type="primary", use_container_width=True): delete_account()

    st.markdown(f"""<div class="hero-container"><div class="homepage-logo">Pro<span>Stock</span></div><p style="font-size:18px; color:#666;">{txt("Hero_Sub")}</p></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        big_search = st.text_input("🔍 " + txt("Search"), placeholder=txt("Search_Ph"), label_visibility="collapsed")
        if big_search:
            q_upper = big_search.upper().strip()
            ticker_res = ASSET_MAP.get(q_upper, q_upper) 
            st.session_state['ticker_search'] = ticker_res
            st.session_state['mode'] = "Asset Terminal"
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.columns(4)
    def render_trend_card(title, assets):
        st.markdown(f"""<div class="trend-card"><div class="trend-header">{title}</div>""", unsafe_allow_html=True)
        for name, sym in assets.items():
            p, chg = get_live_price(sym)
            color = "#00C853" if chg >= 0 else "#D50000"
            st.markdown(f"""<div class="trend-item"><span class="trend-name">{name}</span><span class="trend-price" style="color:{color}">{p:,.2f} ({chg:+.2f}%)</span></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with t1: render_trend_card(txt("Trend_Stocks"), {"NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL", "Samsung": "005930.KS"})
    with t2: render_trend_card(txt("Trend_KR"), {"KOSPI": "^KS11", "KOSDAQ": "^KQ11", "Samsung": "005930.KS", "SK Hynix": "000660.KS"})
    with t3: render_trend_card(txt("Trend_Crypto"), {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "XRP": "XRP-USD"})
    with t4: render_trend_card(txt("Trend_Fx"), {"USD/KRW": "KRW=X", "EUR/USD": "EURUSD=X", "JPY/USD": "JPY=X", "Gold": "GC=F"})
    st.markdown("---")
    st.subheader("📰 Breaking News")
    news_cols = st.columns(2)
    def render_home_news(url):
        items = fetch_rss_feed(url)
        for n in items: 
            st.markdown(f"""<a href='{n['link']}' target='_blank' class='news-card-row'><div class='news-content'><div class='news-title'>{n['title']}</div></div></a>""", unsafe_allow_html=True)
    with news_cols[0]: render_home_news("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664")
    with news_cols[1]: render_home_news("http://rss.cnn.com/rss/money_latest.rss")

# --- MODE: ASSET TERMINAL ---
elif mode == "Asset Terminal":
    main_col, gemini_col = st.columns([3, 1])
    with gemini_col:
        st.markdown(f"""<div class="gemini-box"><div class="gemini-header"><img src="https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg" class="gemini-logo-icon"> &nbsp;Gemini Analyst</div>""", unsafe_allow_html=True)
        
        # API KEY INPUT
        st.text_input("API Key", value=st.session_state.get('gemini_api_key', ''), type="password", key="gemini_api_key", label_visibility="collapsed")

        for msg in st.session_state['chat_history'][-4:]:
            bg = "#e7f1ff" if msg['role']=="ai" else "white"
            align = "left" if msg['role']=="ai" else "right"
            st.markdown(f"""<div class="chat-bubble" style="background:{bg}; text-align:{align}"><b>{msg['role'].upper()}:</b> {msg['content']}</div>""", unsafe_allow_html=True)
        st.text_input("Ask ProStock AI...", key="chat_input_val", on_change=submit_chat)
        st.markdown("<hr>", unsafe_allow_html=True)
        current_ticker = st.session_state.get('ticker_search', 'AAPL')
        symbol_for_widget = current_ticker if "-" not in current_ticker else "NASDAQ:AAPL" 
        if current_ticker.endswith("=X"): symbol_for_widget = f"FX:{current_ticker.replace('=X','')}"
        if current_ticker.endswith("-USD"): symbol_for_widget = f"COINBASE:{current_ticker.replace('-USD','')}USD"
        components.html(f"""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{{"interval": "1m","width": "100%","isTransparent": true,"height": "450","symbol": "{symbol_for_widget}","showIntervalTabs": true,"displayMode": "single","locale": "en","colorTheme": "light"}}</script></div>""", height=460)

    with main_col:
        default_ticker = st.session_state.get('ticker_search', "")
        st.markdown('<div class="prostock-logo" style="font-size:24px;">Pro<span>Stock</span> Terminal</div>', unsafe_allow_html=True)
        search_query = st.text_input(txt("Search"), value=default_ticker, placeholder=txt("Search_Ph"), label_visibility="collapsed")
        ticker = ""; market_type = "Stocks"
        if search_query:
            q_upper = search_query.upper().strip()
            ticker = ASSET_MAP.get(q_upper, q_upper)
            if ticker.endswith("-USD"): market_type = "Crypto"
            elif ticker.endswith("=F"): market_type = "Commodities"
            elif ticker.endswith("=X"): market_type = "Currencies/Forex"
        else:
            market_type_sel = st.sidebar.selectbox("Market Type", [txt("Stocks"), txt("Commodities"), txt("Forex"), txt("Crypto")])
            if market_type_sel == txt("Stocks"): market_type="Stocks"; ticker = st.sidebar.text_input("Ticker", "AAPL").upper()
            elif market_type_sel == txt("Commodities"): market_type="Commodities"; ticker = {"Gold":"GC=F","Silver":"SI=F","Oil":"CL=F"}[st.sidebar.selectbox("Select", ["Gold","Silver","Oil"])]
            elif market_type_sel == txt("Forex"): market_type="Currencies/Forex"; ticker = {"USD/KRW":"KRW=X","EUR/USD":"EURUSD=X"}[st.sidebar.selectbox("Select", ["USD/KRW","EUR/USD"])]
            elif market_type_sel == txt("Crypto"): market_type="Crypto"; ticker = {"Bitcoin":"BTC-USD","Ethereum":"ETH-USD"}[st.sidebar.selectbox("Select", ["Bitcoin","Ethereum"])]
        st.session_state['ticker_search'] = ticker
        user_favs = db[st.session_state['user_id']]['favorites']
        is_fav = ticker in user_favs
        if st.sidebar.checkbox("⭐ Add to Favorites", value=is_fav):
            if not is_fav: db[st.session_state['user_id']]['favorites'].append(ticker)
        else:
            if is_fav: db[st.session_state['user_id']]['favorites'].remove(ticker)
        with st.sidebar.expander("⚙️ Chart Settings", expanded=True):
            timeframe = st.selectbox("Interval", ["1 Minute", "5 Minute", "1 Hour", "1 Day"])
            show_sma = st.toggle("SMA", True); show_bb = st.toggle("Bollinger Bands"); show_rsi = st.toggle("RSI")
        if timeframe == "1 Minute": interval, period = "1m", "1d"
        elif timeframe == "5 Minute": interval, period = "5m", "5d"
        elif timeframe == "1 Hour": interval, period = "1h", "1mo"
        else: interval, period = "1d", "1y"
        if interval == "1d":
            start_date = st.sidebar.date_input("Start", value=datetime.now() - timedelta(days=365))
            end_date = st.sidebar.date_input("End", value=datetime.now())
        if st.sidebar.button("🔄 Refresh Data", type="primary"): st.rerun()

        if ticker:
            try:
                if interval == "1d": data = get_stock_data(ticker, interval, period, start_date, end_date)
                else: data = get_stock_data(ticker, interval, period)
                try: 
                    info = yf.Ticker(ticker).info
                    live_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('ask')
                except: info = {}; live_price = None
                try: news = yf.Ticker(ticker).news
                except: news = []
                if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                data = calculate_technicals(data)
                if not live_price and not data.empty: live_price = data['Close'].iloc[-1]
                curr_p = live_price if live_price else 0.0
                prev_p = data['Close'].iloc[-2] if len(data)>1 else curr_p
                chg = curr_p - prev_p
                pct = (chg/prev_p)*100 if prev_p else 0
                logo_url = info.get('logo_url', '')
                if not logo_url and 'website' in info and info['website']:
                    try: domain = info['website'].split('//')[-1].split('/')[0].replace('www.', ''); logo_url = f"https://logo.clearbit.com/{domain}"
                    except: pass
                logo_html = f'<img src="{logo_url}" class="asset-logo-img">' if logo_url else ''
                curr_code = info.get('currency', 'USD')
                try: krw_rate = yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]
                except: krw_rate = 0
                price_sub = f"(₩{curr_p*krw_rate:,.0f})" if curr_code=='USD' and krw_rate else ""
                st.markdown(f"""
                <div class="finance-header">
                    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                        <div style="display:flex; align-items:center;">{logo_html}<div><h1 style="margin:0;">{ticker}</h1><p style="margin:0;color:#666;">{info.get('shortName', market_type)}</p></div></div>
                        <div style="text-align:right;"><h1 style="margin:0;color:{'#00C853' if chg>=0 else '#D50000'};">{curr_code} {curr_p:,.2f}</h1><p style="margin:0;font-weight:600;color:{'#00C853' if chg>=0 else '#D50000'};">{chg:+.2f} ({pct:+.2f}%) <span style="color:#888;">{price_sub}</span></p></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                tabs = st.tabs([txt("Tab_Chart"), txt("Tab_AI"), txt("Tab_News"), txt("Tab_Data")] + ([txt("Tab_Fund")] if market_type=="Stocks" else []))
                with tabs[0]:
                    fig = go.Figure()
                    if market_type == "Crypto": fig.add_trace(go.Scatter(x=data.index, y=data['Close'], fill='tozeroy', line=dict(color='#2962FF'), name='Price'))
                    else: fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], increasing_line_color='#00C853', decreasing_line_color='#D50000'))
                    if show_sma: fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], line=dict(color='#FFA000', width=1), name='SMA'))
                    if show_bb:
                        fig.add_trace(go.Scatter(x=data.index, y=data['BB_Upper'], line=dict(color='#999', dash='dot'), name='BB Up'))
                        fig.add_trace(go.Scatter(x=data.index, y=data['BB_Lower'], line=dict(color='#999', dash='dot'), name='BB Lo'))
                    rangebreaks = [dict(bounds=["sat", "mon"])] if market_type in ["Stocks", "Commodities"] and interval in ['1m', '5m', '1h'] else []
                    fig.update_layout(height=500, template="plotly_white", xaxis_rangeslider_visible=False, xaxis=dict(rangebreaks=rangebreaks))
                    st.plotly_chart(fig, use_container_width=True)
                with tabs[1]:
                    try: vix = yf.Ticker("^VIX").history(period="5d")['Close'].iloc[-1]; fear_score = max(0, min(100, 100 - (vix - 10) * 2.5)); fg_label = "Fear" if fear_score < 45 else "Greed"
                    except: fear_score=50; fg_label="Neutral"
                    
                    # RESTORED FORECAST CHART
                    if len(data) > 30:
                        df_ml = data[['Close']].dropna().reset_index(); df_ml['i'] = df_ml.index
                        model = LinearRegression().fit(df_ml[['i']], df_ml['Close'])
                        fut_x = np.arange(df_ml['i'].iloc[-1]+1, df_ml['i'].iloc[-1]+31).reshape(-1,1)
                        pred = model.predict(fut_x)
                        fig_p = go.Figure()
                        fig_p.add_trace(go.Scatter(x=df_ml['i'][-50:], y=df_ml['Close'][-50:], name='History'))
                        fig_p.add_trace(go.Scatter(x=fut_x.flatten(), y=pred, name='Forecast', line=dict(dash='dash', color='red')))
                        fig_p.update_layout(height=250, margin=dict(l=0,r=0,t=20,b=0), template="plotly_white", title="30-Period Price Forecast"); st.plotly_chart(fig_p, use_container_width=True)
                        st.caption(f"Projected Trend: **{curr_code} {pred[-1]:.2f}**")
                    else: st.warning("Insufficient data for forecast")
                    
                    report = generate_ai_report(ticker, curr_p, data['SMA'].iloc[-1], data['RSI'].iloc[-1], fear_score, fg_label, "Neutral")
                    st.markdown(f"""<div style="background:#f8f9fa; padding:20px; border-radius:5px; border-left:4px solid #0d6efd;">{report.replace(chr(10), '<br>')}</div>""", unsafe_allow_html=True)
                    
                with tabs[2]:
                    if news:
                        for i in news[:10]:
                            t = safe_extract_news_title(i) or "News"; l = i.get('link') or "#"
                            if 'clickThroughUrl' in i and isinstance(i['clickThroughUrl'], dict): l = i['clickThroughUrl'].get('url', l)
                            st.markdown(f"""<a href='{l}' target='_blank' class='news-card-row'><div class='news-content'><div class='news-title'>{t}</div><div class='news-meta'>Yahoo Finance</div></div></a>""", unsafe_allow_html=True)
                with tabs[3]:
                    st.dataframe(data.tail(50), use_container_width=True)
                    csv = data.to_csv().encode('utf-8')
                    st.download_button("Download CSV", csv, f"{ticker}_data.csv", "text/csv")
                if market_type == "Stocks":
                    with tabs[4]:
                        st.write(f"**Sector:** {info.get('sector', 'N/A')}"); st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                        st.write("**Business Summary:**"); st.write(info.get('longBusinessSummary', 'N/A'))
            except Exception as e: st.error(f"Error loading {ticker}: {e}")

# --- MODE: FAVORITES ---
elif mode == "Favorites":
    st.title(txt("Watchlist"))
    user_favs = db[st.session_state['user_id']]['favorites']
    if not user_favs: st.info("No favorites.")
    else:
        favs = []
        for s in user_favs:
            p, c = get_live_price(s)
            favs.append({"Ticker": s, "Price": f"${p:,.2f}", "Change": f"{c:+.2f}%"})
        st.dataframe(pd.DataFrame(favs), use_container_width=True)

# --- MODE: MEDIA ---
elif mode == "Media & News":
    st.title(txt("Media_Center"))
    st.subheader(txt("Quick"))
    qa1, qa2, qa3 = st.columns(3)
    with qa1: st.link_button("🌐 Investing.com", "https://www.investing.com", use_container_width=True)
    with qa2: st.link_button("📈 Yahoo Finance", "https://finance.yahoo.com", use_container_width=True)
    with qa3: st.link_button("🔎 Google Finance", "https://www.google.com/finance", use_container_width=True)
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: st.subheader("Bloomberg TV"); st.video("https://www.youtube.com/watch?v=iEpJwprxDdk"); st.subheader("Sky News"); st.video("https://www.youtube.com/watch?v=YDvsBbKfLPA")
    with c2: st.subheader("CNA Asia"); st.video("https://www.youtube.com/watch?v=XWq5kBlakcQ"); st.subheader("ABC Australia"); st.video("https://www.youtube.com/watch?v=iipR5yUp36o")
    st.markdown("---")
    def get_feed(url):
        try:
            r = requests.get(url, timeout=3); root = ET.fromstring(r.content)
            return [{'title':i.find('title').text, 'link':i.find('link').text} for i in root.findall('.//item')[:5]]
        except: return []
    t1, t2, t3 = st.tabs(["CNBC", "BBC", "CNN"])
    with t1:
        for n in get_feed("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"): st.markdown(f"<div class='news-list-item'><a href='{n['link']}' target='_blank' class='news-link'>{n['title']}</a></div>", unsafe_allow_html=True)
    with t2:
        for n in get_feed("http://feeds.bbci.co.uk/news/business/rss.xml"): st.markdown(f"<div class='news-list-item'><a href='{n['link']}' target='_blank' class='news-link'>{n['title']}</a></div>", unsafe_allow_html=True)
    with t3:
        for n in get_feed("http://rss.cnn.com/rss/money_latest.rss"): st.markdown(f"<div class='news-list-item'><a href='{n['link']}' target='_blank' class='news-link'>{n['title']}</a></div>", unsafe_allow_html=True)

# --- MODE: MAP ---
elif mode == "Map":
    st.title("🗺️ S&P 500 Map")
    components.html("""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>{"exchanges": [],"dataSource": "SPX500","grouping": "sector","blockSize": "market_cap_basic","blockColor": "change","locale": "en","symbolUrl": "","colorTheme": "light","hasTopBar": false,"isDataSetEnabled": false,"isZoomEnabled": true,"hasSymbolTooltip": true,"width": "100%","height": "800"}</script></div>""", height=810)
    
    st.markdown("---")
    st.subheader("⚡ Instant Access: Top 30 Market Movers")
    top_tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "LLY", "AVGO", "JPM", "V", "UNH", "MA", "XOM", "JNJ", "PG", "HD", "COST", "ABBV", "MRK", "CRM", "AMD", "PEP", "KO", "BAC", "WMT", "CVX", "TMO", "CSCO"]
    cols = st.columns(6)
    for i, t in enumerate(top_tickers):
        with cols[i % 6]:
            try: 
                d = yf.Ticker(t).history(period="1d")
                p = d['Close'].iloc[-1]; c = ((p - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
                label = f"{t}\n{c:+.1f}%"
            except: label = t
            if st.button(label, key=f"map_btn_{t}", use_container_width=True):
                st.session_state['ticker_search'] = t; st.session_state['mode'] = "Asset Terminal"; st.rerun()
