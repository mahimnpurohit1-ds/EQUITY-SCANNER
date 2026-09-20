# scanner.py

import os
import time
import requests
import pandas as pd
from datetime import datetime
import config

# Direct Symbol to Sector Mapping
SECTOR_MAP = {
    # NIFTY BANK & FIN SERVICES
    "HDFCBANK": "Nifty Bank", "ICICIBANK": "Nifty Bank", "SBIN": "Nifty Bank",
    "AXISBANK": "Nifty Bank", "KOTAKBANK": "Nifty Bank", "INDUSINDBK": "Nifty Bank",
    "BANKBARODA": "Nifty Bank", "BAJFINANCE": "Nifty Fin Services",
    "BAJAJFINSV": "Nifty Fin Services", "SHRIRAMFIN": "Nifty Fin Services",

    # NIFTY IT
    "TCS": "Nifty IT", "INFOSYS": "Nifty IT", "HCLTECH": "Nifty IT",
    "WIPRO": "Nifty IT", "LTIM": "Nifty IT", "TECHM": "Nifty IT",
    "PERSISTENT": "Nifty IT", "COFORGE": "Nifty IT",

    # NIFTY AUTO
    "TATAMOTORS": "Nifty Auto", "M&M": "Nifty Auto", "MARUTI": "Nifty Auto",
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

# Upstox API Instrument Keys
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

def fetch_upstox_full_quotes(instrument_keys):
    """Fetches full market quotes (price, volume, VWAP) from Upstox API v2."""
    url = "https://api.upstox.com/v2/market-quote/quotes"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {config.UPSTOX_ACCESS_TOKEN}'
    }
    params = {'instrument_key': ','.join(instrument_keys)}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            print(f"[Upstox API Error] Status Code {response.status_code}: {response.text}")
            return {}
    except Exception as e:
        print(f"Connection Error: {e}")
        return {}

def process_market_data():
    data = fetch_upstox_full_quotes(INSTRUMENT_KEYS)
    
    all_stocks = []
    qualified_matches = []
    
    for raw_key, val in data.items():
        symbol = raw_key.replace(':', '|').split('|')[-1]
        sector = SECTOR_MAP.get(symbol, "Other")
        
        ohlc = val.get('ohlc', {})
        open_price = ohlc.get('open', 0.0)
        close_price = ohlc.get('close', 0.0)
        last_price = val.get('last_price', open_price)
        volume = val.get('volume', 0)
        vwap = val.get('average_price', open_price)
        
        if vwap == 0:
            vwap = open_price
            
        if close_price > 0 and open_price > 0:
            gap_pct = round(((open_price - close_price) / close_price) * 100, 2)
            
            all_stocks.append({
                'Symbol': symbol,
                'Sector': sector,
                'Open': open_price,
                'Close': close_price,
                'Gap_Pct': gap_pct,
                'Volume': volume,
                'VWAP': vwap
            })
            
            # 1.6% PROFIT STRATEGY CONDITIONS
            is_gap_valid = (1.0 <= gap_pct <= 2.5)
            is_volume_valid = (volume >= config.MIN_VOLUME_THRESHOLD)
            is_vwap_valid = (open_price >= vwap or last_price >= vwap)
            
            if is_gap_valid and is_volume_valid and is_vwap_valid:
                target_price = round(open_price * (1 + config.TARGET_PCT), 2)
                stop_loss_price = round(open_price * (1 - config.STOP_LOSS_PCT), 2)
                
                risk_per_share = open_price - stop_loss_price
                qty = int(config.MAX_RISK_PER_TRADE / risk_per_share) if risk_per_share > 0 else 1
                
                qualified_matches.append({
                    'Symbol': symbol,
                    'Sector': sector,
                    'Price (₹)': open_price,
                    'Gap (%)': f"+{gap_pct:.2f}%",
                    'Volume': f"{volume:,}",
                    'VWAP (₹)': vwap,
                    'Target +1.6% (₹)': target_price,
                    'Stop Loss -0.8% (₹)': stop_loss_price,
                    'Qty': qty,
                    'Signal': 'BUY (1.6% Target)'
                })

    df_all = pd.DataFrame(all_stocks)
    df_qualified = pd.DataFrame(qualified_matches)
    
    return df_all, df_qualified

def generate_sector_summaries(df_all):
    if df_all.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    sector_summary = df_all.groupby('Sector')['Gap_Pct'].mean().reset_index()
    sector_summary.columns = ['Sector', 'Avg Gap (%)']
    sector_summary['Avg Gap (%)'] = sector_summary['Avg Gap (%)'].round(2)
    
    df_gainers = sector_summary[sector_summary['Avg Gap (%)'] >= 0].sort_values(by='Avg Gap (%)', ascending=False)
    df_losers = sector_summary[sector_summary['Avg Gap (%)'] < 0].sort_values(by='Avg Gap (%)', ascending=True)
    
    df_gainers['Avg Gap (%)'] = df_gainers['Avg Gap (%)'].apply(lambda x: f"+{x:.2f}%")
    df_losers['Avg Gap (%)'] = df_losers['Avg Gap (%)'].apply(lambda x: f"{x:.2f}%")
    
    return df_gainers, df_losers

if __name__ == "__main__":
    print("Starting Live 1.6% Strategy Scanner (Auto-refreshing every 10s)... Press Ctrl+C to stop.\n")
    
    while True:
        try:
            # Clear terminal screen for a clean live dashboard look
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("=" * 110)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] LIVE EQUITY SCANNER (Auto-refreshing every 10 seconds)")
            print("=" * 110 + "\n")
            
            df_all, df_qualified = process_market_data()
            
            if not df_all.empty:
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', 1000)
                
                df_gainers, df_losers = generate_sector_summaries(df_all)
                
                # TABLE 1: GAINING SECTORS
                print("=" * 60)
                print("                 OVERALL GAINING SECTORS                    ")
                print("=" * 60)
                print(df_gainers.to_string(index=False) if not df_gainers.empty else "No sectors in positive gain right now.")
                print("=" * 60 + "\n")
                
                # TABLE 2: LOSING SECTORS
                print("=" * 60)
                print("                 OVERALL LOSING SECTORS                    ")
                print("=" * 60)
                print(df_losers.to_string(index=False) if not df_losers.empty else "No losing sectors.")
                print("=" * 60 + "\n")
                
                # TABLE 3: QUALIFIED 1.6% PROFIT STRATEGY MATCHES
                print("=" * 110)
                print("            QUALIFIED STOCKS MEETING ALL 1.6% PROFIT STRATEGY CONDITIONS            ")
                print("=" * 110)
                if not df_qualified.empty:
                    print(df_qualified.to_string(index=False))
                    df_qualified.to_csv("strategy_1.6pct_watchlist.csv", index=False)
                    print("\n[SUCCESS] Saved updated signals to 'strategy_1.6pct_watchlist.csv'.")
                else:
                    print("No stocks satisfy all conditions right now (1.0%-2.5% Gap Up + Vol >= 50k + Price >= VWAP).")
                print("=" * 110)
            else:
                print("Could not retrieve market quote data. Please verify your UPSTOX_ACCESS_TOKEN in config.py.")
                
            time.sleep(10)  # Wait 10 seconds before refreshing live market data
            
        except KeyboardInterrupt:
            print("\n[STOPPED] Scanner stopped by user.")
            break