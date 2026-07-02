import requests
import xml.etree.ElementTree as ET
import json
from pathlib import Path

def fetch_silver_news_rss():
    print("Starte Abruf der Silber-News via Yahoo RSS...")
    
    # Der offizielle Yahoo Finance RSS-Feed für den Silber-Future (SI=F) und den ETF (SLV)
    url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=SI=F,SLV"
    
    # Headers mitsenden, damit Yahoo uns nicht für einen bösartigen Bot hält
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Prüft, ob die Verbindung geklappt hat
        
        # Das XML von Yahoo parsen (lesen)
        root = ET.fromstring(response.content)
        silver_news = []
        
        # Wir suchen nach allen Nachrichten-Einträgen (<item>) im Feed
        # und nehmen direkt die ersten 10
        for item in root.findall('.//item')[:10]:
            title = item.find('title').text if item.find('title') is not None else "Kein Titel"
            link = item.find('link').text if item.find('link') is not None else "#"
            
            silver_news.append({
                "tag": "SILVER",
                "title": title,
                "url": link
            })
            
        # Datei schreiben
        output_file = Path(__file__).parent / "silver_news.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(silver_news, f, indent=4, ensure_ascii=False)
            
        print(f"[+] {len(silver_news)} Silber-News erfolgreich aus dem Yahoo RSS-Feed gezogen!")
        
    except Exception as e:
        print(f"[!] Kritischer Fehler beim RSS-Abruf: {e}")

if __name__ == "__main__":
    fetch_silver_news_rss()