# dashboard.py

import os
import requests
import pandas as pd
from datetime import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import config

st.set_page_config(
    page_title="1.6% Strategy Live Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sector Mapping
SECTOR_MAP = {
    # NIFTY BANK & FIN SERVICES
    "HDFCBANK": "Nifty Bank", "ICICIBANK": "Nifty Bank", "SBIN": "Nifty Bank",
    "AXISBANK": "Nifty Bank", "KOTAKBANK": "Nifty Bank", "INDUSINDBK": "Nifty Bank",
    "BANKBARODA": "Nifty Bank", "BAJFINANCE": "Nifty Fin Services",
    "BAJAJFINSV": "Nifty Fin Services", "SHRIRAMFIN": "Nifty Fin Services",

    # NIFTY IT
    "TCS": "Nifty IT", "INFOSYS": "Nifty IT", "INFY": "Nifty IT", "HCLTECH": "Nifty IT",
    "WIPRO": "Nifty IT", "LTIM": "Nifty IT", "TECHM": "Nifty IT",
    "PERSISTENT": "Nifty IT", "COFORGE": "Nifty IT",

    # NIFTY AUTO
    "TATAMOTORS": "Nifty Auto", "TMPV": "Nifty Auto", "M&M": "Nifty Auto", "MARUTI": "Nifty Auto",
    "BAJAJ-AUTO": "Nifty Auto", "HEROMOTOCO": "Nifty Auto", "EICHERMOT": "Nifty Auto",

    # NIFTY FMCG
    "ITC": "Nifty FMCG", "HINDUNILVR": "Nifty FMCG", "NESTLEIND": "Nifty FMCG",
    "BRITANNIA": "Nifty FMCG", "TATACONSUM": "Nifty FMCG", "DABUR": "Nifty FMCG",
    "GODREJCP": "Nifty FMCG", "VBL": "Nifty FMCG",

    # NIFTY PHARMA
    "SUNPHARMA": "Nifty Pharma", "DRREDDY": "Nifty Pharma", "CIPLA": "Nifty Pharma",
    "DIVISLAB": "Nifty Pharma", "ZYDUSLIFE": "Nifty Pharma", "TORNTPHARM": "Nifty Pharma",

    # NIFTY METAL
    "TATASTEEL": "Nifty Metal", "HINDALCO": "Nifty Metal", "JSWSTEEL": "Nifty Metal",
    "COALINDIA": "Nifty Metal", "VEDL": "Nifty Metal",

    # NIFTY REALTY
    "DLF": "Nifty Realty", "LODHA": "Nifty Realty", "GODREJPROP": "Nifty Realty",
    "OBEROIRLTY": "Nifty Realty",

    # CEMENTS
    "ULTRACEMCO": "Nifty Cements", "GRASIM": "Nifty Cements", "AMBUJACEM": "Nifty Cements",
    "ACC": "Nifty Cements", "SHREECEM": "Nifty Cements"
}

INSTRUMENT_KEYS = [
    "NSE_EQ|INE040A01034", "NSE_EQ|INE090A01021", "NSE_EQ|INE062A01020", "NSE_EQ|INE238A01034",
    "NSE_EQ|INE237A01028", "NSE_EQ|INE095A01012", "NSE_EQ|INE028A01039", "NSE_EQ|INE296A01024",
    "NSE_EQ|INE918I01026", "NSE_EQ|INE721A01013", "NSE_EQ|INE467B01029", "NSE_EQ|INE009A01021",
    "NSE_EQ|INE860A01027", "NSE_EQ|INE075A01022", "NSE_EQ|INE214T01019", "NSE_EQ|INE669C01036",
    "NSE_EQ|INE262H01013", "NSE_EQ|INE591G01017", "NSE_EQ|INE155A01022", "NSE_EQ|INE101A01026",
    "NSE_EQ|INE585B01010", "NSE_EQ|INE917I01010", "NSE_EQ|INE158A01026", "NSE_EQ|INE066A01021",
    "NSE_EQ|INE154A01025", "NSE_EQ|INE121A01024", "NSE_EQ|INE239A01024", "NSE_EQ|INE216A01030",
    "NSE_EQ|INE192A01025", "NSE_EQ|INE016A01026", "NSE_EQ|INE102D01028", "NSE_EQ|INE200M01021",
    "NSE_EQ|INE044A01036", "NSE_EQ|INE089A01023", "NSE_EQ|INE059A01026", "NSE_EQ|INE361B01024",
    "NSE_EQ|INE010B01027", "NSE_EQ|INE685A01022", "NSE_EQ|INE081A01020", "NSE_EQ|INE038A01020",
    "NSE_EQ|INE019A01038", "NSE_EQ|INE522F01014", "NSE_EQ|INE205A01025", "NSE_EQ|INE271C01023",
    "NSE_EQ|INE670K01029", "NSE_EQ|INE484J01027", "NSE_EQ|INE093I01010", "NSE_EQ|INE481G01011",
    "NSE_EQ|INE047A01021", "NSE_EQ|INE079A01024", "NSE_EQ|INE012A01025", "NSE_EQ|INE070A01015"
]

def fetch_upstox_full_quotes():
    url = "https://api.upstox.com/v2/market-quote/quotes"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {config.UPSTOX_ACCESS_TOKEN}'
    }
    params = {'instrument_key': ','.join(INSTRUMENT_KEYS)}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return {}
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return {}

def process_market_data():
    data = fetch_upstox_full_quotes()
    all_stocks, qualified_matches = [], []
    
    for raw_key, val in data.items():
        symbol = raw_key.replace(':', '|').split('|')[-1]
        sector = SECTOR_MAP.get(symbol, "Other")
        
        ohlc = val.get('ohlc', {})
        open_price = ohlc.get('open', 0.0)
        close_price = ohlc.get('close', 0.0)  # Yesterday's close
        last_price = val.get('last_price', open_price)  # Current Live Price (LTP)
        volume = val.get('volume', 0)
        vwap = val.get('average_price', open_price)
        if vwap == 0: vwap = open_price
            
        if close_price > 0 and open_price > 0 and last_price > 0:
            # Real-time Live Change % (Current Price vs Yesterday's Close)
            live_change_pct = round(((last_price - close_price) / close_price) * 100, 2)
            
            # Opening Gap % (Open vs Yesterday's Close)
            gap_pct = round(((open_price - close_price) / close_price) * 100, 2)
            
            # Intraday Move % (Current Price vs Open Price)
            move_from_open_pct = round(((last_price - open_price) / open_price) * 100, 2)
            
            all_stocks.append({
                'Symbol': symbol,
                'Sector': sector,
                'LTP / Live (₹)': last_price,
                'Live Up/Down (%)': live_change_pct,
                'Open (₹)': open_price,
                'Prev Close (₹)': close_price,
                'Move from Open (%)': move_from_open_pct,
                'Volume': volume,
                'VWAP (₹)': round(vwap, 2)
            })
            
            # STRATEGY FILTERS:
            is_gap_valid = (1.0 <= gap_pct <= 2.5)
            is_volume_valid = (volume >= config.MIN_VOLUME_THRESHOLD)
            is_vwap_valid = (last_price >= vwap)
            
            # Stock MUST be trading AT or ABOVE its Open price (Prevents buying falling stocks)
            is_moving_up = (last_price >= open_price)
            
            if is_gap_valid and is_volume_valid and is_vwap_valid and is_moving_up:
                target_price = round(last_price * (1 + config.TARGET_PCT), 2)
                stop_loss_price = round(last_price * (1 - config.STOP_LOSS_PCT), 2)
                risk_per_share = last_price - stop_loss_price
                qty = int(config.MAX_RISK_PER_TRADE / risk_per_share) if risk_per_share > 0 else 1
                
                qualified_matches.append({
                    'Symbol': symbol,
                    'Sector': sector,
                    'LTP / Live Price (₹)': last_price,
                    'Live Up/Down (%)': live_change_pct,
                    'Move from Open (%)': move_from_open_pct,
                    'Volume': volume,
                    'VWAP (₹)': round(vwap, 2),
                    'Target +1.6% (₹)': target_price,
                    'Stop Loss -0.8% (₹)': stop_loss_price,
                    'Quantity': qty,
                    'Signal': 'BUY'
                })

    return pd.DataFrame(all_stocks), pd.DataFrame(qualified_matches)

# --- SIDEBAR CONTROLS ---
st.sidebar.title("⚙️ Control Panel")
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", min_value=5, max_value=60, value=10, step=5)
st_autorefresh(interval=refresh_rate * 1000, key="datarefresh")

st.sidebar.markdown("---")
st.sidebar.subheader("Strategy Thresholds")
st.sidebar.write(f"• **Target:** +{config.TARGET_PCT * 100:.1f}%")
st.sidebar.write(f"• **Stop Loss:** -{config.STOP_LOSS_PCT * 100:.1f}%")
st.sidebar.write(f"• **Max Risk/Trade:** ₹{config.MAX_RISK_PER_TRADE}")
st.sidebar.write(f"• **Min Volume:** {config.MIN_VOLUME_THRESHOLD:,}")

# --- HEADER SECTION ---
st.title("📈 Live Stock Performance & Strategy Dashboard")
st.caption(f"Last updated at: **{datetime.now().strftime('%H:%M:%S IST')}** | Refreshing every {refresh_rate}s")

df_all, df_qualified = process_market_data()

# --- TOP STATS METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Stocks Monitored", value=len(df_all))

with col2:
    signal_count = len(df_qualified)
    st.metric(label="Qualified BUY Signals", value=signal_count, delta=f"{signal_count} Opportunities" if signal_count > 0 else "0 Opportunities")

with col3:
    if not df_all.empty:
        top_stock = df_all.sort_values(by='Live Up/Down (%)', ascending=False).iloc[0]
        st.metric(label="Top Live Gainer", value=top_stock['Symbol'], delta=f"+{top_stock['Live Up/Down (%)']:.2f}%")

with col4:
    if not df_all.empty:
        worst_stock = df_all.sort_values(by='Live Up/Down (%)', ascending=True).iloc[0]
        st.metric(label="Top Live Loser", value=worst_stock['Symbol'], delta=f"{worst_stock['Live Up/Down (%)']:.2f}%", delta_color="inverse")

st.markdown("---")

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 Qualified Trades (BUY Signals)", "📊 Sector Performance", "🔍 Full Live Market List"])

with tab1:
    st.subheader("🎯 Active Trading Signals (Only Stocks Currently Moving Up)")
    if not df_qualified.empty:
        st.success(f"Found {len(df_qualified)} stocks matching all criteria & currently holding/gaining above Open!")
        st.dataframe(
            df_qualified.style.format({
                'LTP / Live Price (₹)': '₹{:.2f}',
                'Live Up/Down (%)': '{:+.2f}%',
                'Move from Open (%)': '{:+.2f}%',
                'Volume': '{:,}',
                'VWAP (₹)': '₹{:.2f}',
                'Target +1.6% (₹)': '₹{:.2f}',
                'Stop Loss -0.8% (₹)': '₹{:.2f}',
            }),
            use_container_width=True
        )
    else:
        st.info("No stocks currently satisfy all criteria (Gap 1-2.5% + Trading ABOVE Open + Above VWAP + High Vol).")

with tab2:
    st.subheader("📈 Sector Average Live Performance")
    if not df_all.empty:
        sector_summary = df_all.groupby('Sector')['Live Up/Down (%)'].mean().reset_index()
        sector_summary.columns = ['Sector', 'Avg Live Change (%)']
        sector_summary = sector_summary.sort_values(by='Avg Live Change (%)', ascending=False)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("### Sector Live Ranking")
            st.dataframe(
                sector_summary.style.format({'Avg Live Change (%)': '{:+.2f}%'}),
                use_container_width=True
            )
        with c2:
            st.markdown("### Visual Sector Breakdown")
            st.bar_chart(sector_summary.set_index('Sector'))

with tab3:
    st.subheader("📋 All Scanned Stocks (Live Prices & % Up/Down)")
    if not df_all.empty:
        search = st.text_input("Search Symbol or Sector:", "")
        filtered_df = df_all[
            df_all['Symbol'].str.contains(search.upper()) | 
            df_all['Sector'].str.contains(search, case=False)
        ]
        
        filtered_df = filtered_df.sort_values(by='Live Up/Down (%)', ascending=False)
        
        st.dataframe(
            filtered_df.style.format({
                'LTP / Live (₹)': '₹{:.2f}',
                'Live Up/Down (%)': '{:+.2f}%',
                'Open (₹)': '₹{:.2f}',
                'Prev Close (₹)': '₹{:.2f}',
                'Move from Open (%)': '{:+.2f}%',
                'Volume': '{:,}',
                'VWAP (₹)': '₹{:.2f}'
            }),
            use_container_width=True
        )