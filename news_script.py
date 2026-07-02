import requests
import pandas as pd
import json
import yfinance as yf
from pathlib import Path

# ==========================================
# 1. KONFIGURATION & API-KEYS
# ==========================================
# Hinweis: API-Key vor dem Git-Push idealerweise in eine .env auslagern.
FINNHUB_KEY = "Dein API Key"


# ==========================================
# 2. ABFRAGE-FUNKTIONEN (Extract & Transform)
# ==========================================

def fetch_finnhub_news():
    """Holt die aktuellsten, allgemeinen Markt-News von Finnhub (Wall Street Fokus)"""
    news_list = []
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            for article in data[:20]:
                news_list.append({
                    "publisher": article.get("source", "FINNHUB"),
                    "title": article.get("headline", ""),
                    "url": article.get("url", "")
                })
        else:
            print(f"[-] Finnhub Fehler (Code {response.status_code}): {response.text}")

    except Exception as e:
        print(f"[!] Fehler bei Finnhub: {e}")

    return news_list


def _parse_yfinance_article(article):
    """
    Defensiver Parser für yfinance-News-Items.
    yfinance hat das Response-Format Anfang 2025 umgestellt: Neues Format hat
    ein verschachteltes 'content'-Objekt. Wir behandeln beide Varianten.
    """
    # --- Neues Format ---
    if isinstance(article, dict) and "content" in article and isinstance(article["content"], dict):
        c = article["content"]
        title = c.get("title", "")

        url = ""
        if c.get("canonicalUrl"):
            url = c["canonicalUrl"].get("url", "")
        elif c.get("clickThroughUrl"):
            url = c["clickThroughUrl"].get("url", "")

        publisher = "YAHOO"
        if c.get("provider"):
            publisher = c["provider"].get("displayName", "YAHOO")

        return {"publisher": publisher, "title": title, "url": url}

    # --- Altes Format als Fallback ---
    return {
        "publisher": article.get("publisher", "YAHOO"),
        "title": article.get("title", ""),
        "url": article.get("link", "")
    }


def fetch_yfinance_news():
    """Holt News zu Leitindizes über das Yahoo Finance Netzwerk"""
    news_list = []
    # Leitindizes: USA, Europa, Rohstoffe, Krypto
    symbols = ["^GSPC", "^GDAXI", "GC=F", "BTC-USD"]

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news or []

            for article in news:
                news_list.append(_parse_yfinance_article(article))
        except Exception as e:
            print(f"[-] Fehler beim News-Abruf für {symbol} via yfinance: {e}")

    return news_list


# ==========================================
# 3. DATEN-PIPELINE & PANDAS (Deduplication)
# ==========================================

def build_news_pipeline():
    print("Starte reine Finanz-News-Pipeline...")

    all_news = fetch_finnhub_news() + fetch_yfinance_news()

    if not all_news:
        print("Keine News gefunden. Bitte API-Keys und Internetverbindung prüfen.")
        return

    df = pd.DataFrame(all_news)

    # Bereinigung: leere Einträge entfernen
    df_clean = df.dropna(subset=['title', 'url'])
    df_clean = df_clean[df_clean['title'].astype(str).str.strip() != ""]
    df_clean = df_clean[df_clean['url'].astype(str).str.strip() != ""]

    # Duplikate anhand des Titels entfernen
    df_clean = df_clean.drop_duplicates(subset=['title'], keep='first')

    # Auf 25 neueste/relevanteste begrenzen
    df_final = df_clean.head(25)

    final_news_list = df_final.to_dict(orient='records')

    # ==========================================
    # 4. EXPORT (Load)
    # ==========================================
    # FIX: Pfad relativ zum Script-Ordner (nicht zum cwd)
    base_dir = Path(__file__).parent
    output_file = base_dir / "news.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_news_list, f, indent=4, ensure_ascii=False)

    print(f"[+] Erfolgreich {len(final_news_list)} hochrelevante Finanz-News gespeichert in: {output_file.absolute()}")


if __name__ == "__main__":
    pd.options.mode.chained_assignment = None
    build_news_pipeline()
