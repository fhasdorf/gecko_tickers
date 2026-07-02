import yfinance as yf
import json
import time
import pandas as pd
import math
from pathlib import Path

# --- MASTER TICKER LISTE FÜR MERIDIANA ---
TICKERS = {

    # Einzel-Nebenwerte 
    # TIPP: Füge hier einfach 10-20 weitere Werte hinzu, damit die Boxen gut gefüllt sind!
    "[DUS] The New Meat Co": "9AUA.DU",
    "[FRA] Crypto Blockchain Indust. S.A": "7DO0.F",
    "[NDAQ] Hyperliquid Strategies Inc.": "PURR",
    "[CRP] Hyperliquid USD": "HYPE32196-USD",
    "[FRA] St George Mining Limited": "S0G.F",

     # Indizes (werden im Ticker gezeigt, aber für Top/Flop aussortiert)
    "[DE] SDAX": "^SDAXI",
    "[DE] TecDAX": "^TECDAX",
    "[NDAQ] Nasdaq Composite": "^IXIC",
}


def fetch_ticker_data():
    results = []
    
    for name, symbol in TICKERS.items():
        try:
            print(f"Frage ab: {name} ({symbol})...")
            ticker = yf.Ticker(symbol)
            
            hist = ticker.history(period="1mo")
            info = ticker.info
            
            bid = info.get('bid', 0.0)
            ask = info.get('ask', 0.0)
            if bid is None: bid = 0.0
            if ask is None: ask = 0.0
            
            current_price = None
            prev_close = None
            
            if not hist.empty and len(hist) >= 1:
                current_price = float(hist['Close'].iloc[-1])
                if len(hist) > 1:
                    prev_close = float(hist['Close'].iloc[-2])
                else:
                    prev_close = current_price
            else:
                raw_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                if raw_price is not None and raw_price > 0:
                    current_price = float(raw_price)
                    prev_close = current_price
                else:
                    print(f"   [-] Übersprungen: {name} (Kein Kurs)")
                    continue

            # --- SICHERHEITS-CHECKS & BERECHNUNG ---
            if pd.isna(current_price) or pd.isna(prev_close) or prev_close == 0:
                print(f"   [-] Übersprungen: {name} (Lückenhafte Daten)")
                continue            
            
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            if math.isnan(change_pct) or math.isinf(change_pct):
                print(f"   [-] Übersprungen: {name} (Berechnungsfehler)")
                continue
            
            if change_pct > 0:
                trend_class = "ticker-up"
                arrow = "▲"
                change_str = f"+{change_pct:.2f}%"
            elif change_pct < 0:
                trend_class = "ticker-down"
                arrow = "▼"
                change_str = f"{change_pct:.2f}%"
            else:
                trend_class = "ticker-neutral"
                arrow = "▶"
                change_str = "0.00%"
                
            is_stock = not symbol.startswith("^")
                
            results.append({
                "name": name,
                "price": current_price, 
                "change_pct_str": change_str,
                "raw_change_pct": change_pct, # NEU: Der rohe Float-Wert für unsere Sortierung
                "arrow": arrow,
                "trend_class": trend_class,
                "bid": bid,
                "ask": ask,
                "is_stock": is_stock
            })
            
        except Exception as e:
            print(f"   [!] Fehler beim Abruf von {symbol}: {e}")
        
        time.sleep(0.5)

        
    # --- 1. EXPORT: DER NORMALE TICKER (kurse.json) ---
    base_dir = Path(__file__).parent
    kurse_file = base_dir / "kurse.json"
    
    try:
        with open(kurse_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, allow_nan=False)
        print(f"\nErfolgreich {len(results)} Kurse in kurse.json aktualisiert.")
    except ValueError as e:
        print(f"\n[!] Kritischer Fehler beim Export der kurse.json: {e}")

    # --- 2. DATEN-TRANSFORMATION FÜR DIE BOXEN ---
    # Wir filtern die Indizes heraus, da wir in den Top/Flops nur echte Aktien sehen wollen
    stocks_only = [item for item in results if item["is_stock"]]
    
    # TOP GEWINNER: Absteigend sortieren (höchster Wert zuerst)
    top_gewinner = sorted(stocks_only, key=lambda x: x["raw_change_pct"], reverse=True)[:3]
    
    # TOP VERLIERER: Aufsteigend sortieren (tiefster Wert zuerst)
    top_verlierer = sorted(stocks_only, key=lambda x: x["raw_change_pct"])[:3]
    
    # TRENDING (Volatilität): Nach absolutem Wert sortieren (höchster Ausschlag, egal ob + oder -)
    trending = sorted(stocks_only, key=lambda x: abs(x["raw_change_pct"]), reverse=True)[:3]

    boxes_data = {
        "gewinner": top_gewinner,
        "verlierer": top_verlierer,
        "trending": trending
    }


    # --- 3. EXPORT: DIE BOXEN (boxes.json) ---
    boxes_file = base_dir / "boxes.json"
    try:
        with open(boxes_file, "w", encoding="utf-8") as f:
            json.dump(boxes_data, f, indent=4, allow_nan=False)
        print(f"Erfolgreich Top/Flop/Trending in boxes.json generiert.")
    except ValueError as e:
        print(f"[!] Kritischer Fehler beim Export der boxes.json: {e}")

if __name__ == "__main__":
    print("Starte Kurs-Abruf via yfinance...\n")
    fetch_ticker_data()