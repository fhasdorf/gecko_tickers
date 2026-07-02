# gecko_tickers
Configurable Oldskool 90s Multilane Stock &amp; Newstickers

Ein modulares, webbasiertes Finanz-Terminal mit Oldschool-Laufschriften (Tickern) und automatisierten Daten-Pipelines. Ideal für Websites, Dashboards oder Info-Screens.

## ✨ Features
* **Multi-Lane Ticker:** Mehrere horizontal scrollende Bänder mit unterschiedlichen Geschwindigkeiten (CSS-animiert).
* **Top/Flop/Trending Boxen:** Automatische Auswertung der Gewinner, Verlierer und stärksten Ausreißer des Tages aus einem frei definierbaren Aktien-Pool.
* **Load-Randomization:** Zufällige Anordnung der Ticker- und News-Werte bei jedem Seitenaufruf für ein dynamisches Leseerlebnis.
* **Automatisierte Pipelines:** Unabhängige Python-Scripte (ETL) sammeln Kursdaten, News und Börsengänge und stellen diese als leichtgewichtige JSON-Dateien für das Frontend bereit.

## 🏗️ Architektur & Datenquellen
Das Terminal bezieht seine Daten dezentral über verschiedene Methoden. So wird Ausfallsicherheit gewährleistet und API-Limits werden geschont:

1. **Aktienkurse & Indizes (`ticker_script.py`):**
   * *Quelle:* Yahoo Finance API (via `yfinance` Bibliothek).
   * *Funktion:* Lädt historische Kurse, Bid/Ask-Spreads und berechnet prozentuale Veränderungen. Filtert Indizes für die Top/Flop-Boxen automatisch heraus.
2. **Allgemeine Finanz-News (`news_script.py`):**
   * *Quellen:* Finnhub API (Marktnews) + Yahoo Finance (`yfinance` für Leitindizes wie S&P500, DAX, Gold, Bitcoin).
   * *Funktion:* Führt die Datenströme zusammen, bereinigt sie (Pandas), entfernt Duplikate und exportiert die 25 relevantesten Artikel.
3. **Rohstoff-News (Silber) (`silver_news_script.py`):**
   * *Quelle:* Yahoo Finance RSS-Feed.
   * *Funktion:* Liest und parst den klassischen XML-Feed für die Tickersymbole `SI=F` (Future) und `SLV` (ETF).
4. **Börsengänge / IPOs (`ipo_script.py`):**
   * *Quelle:* Börse Düsseldorf (Web Scraping).
   * *Funktion:* Scraping der HTML-Tabelle für Neueinführungen der letzten 5 Tage mithilfe von BeautifulSoup.

## 🛠️ Anpassung & Eigene Werte (Customization)
Das System ist darauf ausgelegt, unkompliziert erweitert zu werden. Hier sind die wichtigsten Stellschrauben:

### 1. Eigene Aktien & Indizes hinzufügen
Öffne die Datei `ticker_script.py` und suche das Dictionary `TICKERS`. Füge neue Werte nach dem Schema `"[Anzeigename]": "[Yahoo-Finance-Symbol]"` hinzu:

```
python
TICKERS = {
    "[DE] SAP": "SAP.DE",
    "[US] Apple": "AAPL",
    "[KRYPTO] Ethereum": "ETH-USD",
    # Hier beliebig viele Werte ergänzen...
}
```

### 2. News-Quellen anpassen

* Andere Indizes für News: In news_script.py kannst du die Liste symbols = ["^GSPC", "^GDAXI", "GC=F", "BTC-USD"] um beliebige Yahoo-Ticker ergänzen.
* Anderer RSS-Feed: In silver_news_script.py einfach die url Variable austauschen (z. B. gegen einen Gold- oder Krypto-RSS-Feed).

### 3. Design & Farben ändern
Alle visuellen Anpassungen finden in ticker2.html im <style> Block statt:

* Hintergrundfarben: body { background-color: #121518; }
* Ticker-Geschwindigkeiten: Passe die @keyframes oder die Dauer in den Klassen an, z. B. .ticker-speed-fast { animation: ticker-scroll 35s ... }
    
## 🚀 4. Installation & Deployment

### 1. Voraussetzungen installieren:
Es wird Python 3.x benötigt. Installiere die Abhängigkeiten über:

    '''
    pip install requests beautifulsoup4 pandas yfinance
    '''
### 2. ⚠️ API Keys konfigurieren (Wichtig für Public Repos):
Achtung: In news_script.py wird ein Finnhub API-Key (FINNHUB_KEY) verwendet. Bevor du das Projekt produktiv setzt, solltest du diesen Key idealerweise über eine .env Datei oder als Server-Umgebungsvariable laden, um Missbrauch zu vermeiden.

### 3. Automatisierung (Cronjobs):
Damit das Terminal immer aktuelle Daten zeigt, müssen die Python-Scripte regelmäßig im Hintergrund ausgeführt werden. Empfohlen ist die Einrichtung von Cronjobs (z. B. auf einem Variomedia-Server oder einem anderen Linux-Host):

    '''
    # Kurse alle 10 Minuten aktualisieren
    */10 * * * * cd /pfad/zum/ordner && python3 ticker_script.py
    
    # Allgemeine News einmal pro Stunde aktualisieren
    0 * * * * cd /pfad/zum/ordner && python3 news_script.py
    
    # RSS-Feeds alle 3 Stunden prüfen
    0 */3 * * * cd /pfad/zum/ordner && python3 silver_news_script.py
    
    # IPOs einmal täglich um 08:00 Uhr abrufen
    0 8 * * * cd /pfad/zum/ordner && python3 ipo_script.py
    '''

### 📦 Externe Bibliotheken (Drittanbieter)
Diese Pakete bilden den Kern deiner Daten-Pipeline und müssen über den Paketmanager (pip) installiert werden:
* yfinance: Das Herzstück für den Kursabruf (ticker_script.py). Es klinkt sich in die inoffizielle Yahoo Finance API ein, um historische Marktdaten, Live-Kurse und Spread-Informationen (Bid/Ask) zu ziehen.
* pandas: Ein mächtiges Data-Science-Werkzeug, das hier in news_script.py für die Datenmanipulation genutzt wird. Es ist ideal, um die gesammelten Nachrichten aus verschiedenen Quellen in einen DataFrame zu laden, leere Einträge zu bereinigen und Duplikate sauber herauszufiltern.
* requests: Der Standard für HTTP-Anfragen in Python. Es wird in fast allen Scripten genutzt, um externe Server anzusprechen (die Finnhub API, den Yahoo RSS Feed und die Website der Börse Düsseldorf).
* beautifulsoup4 (im Code als bs4 importiert): Wird im ipo_script.py verwendet. Es analysiert (parst) den rohen HTML-Code der Börse Düsseldorf, damit du gezielt die Tabelle mit den Neueinführungen auslesen kannst.

### 🛠️ Python Standard-Bibliotheken
Diese Module sind bereits fest in Python integriert und erfordern keine Installation. Sie übernehmen die administrativen und logischen Hintergrundaufgaben:
* json: Zwingend notwendig für alle Scripte, um die gesammelten und transformierten Daten in das leichtgewichtige JSON-Format zu übersetzen, welches das HTML-Frontend lesen kann.
* pathlib: Sorgt für saubere, dynamische und systemübergreifende Dateipfade (z. B. Path(__file__).parent). Das verhindert Fehler, egal von wo aus das Script aufgerufen wird.
* datetime / time: Wird genutzt, um Datums-Filter zu setzen (z. B. "nur IPOs der letzten 5 Tage") und um kurze Pausen (time.sleep) zwischen den API-Aufrufen einzubauen, damit Server dich nicht blockieren.
* xml.etree.ElementTree: Ein eingebauter XML-Parser, der in silver_news_script.py genutzt wird, um die Struktur des klassischen Yahoo RSS-Feeds aufzubrechen und die Artikel-Links zu extrahieren.
* math: Wird im Ticker-Script verwendet, um mathematische Ausnahmefehler (wie NaN oder unendliche Werte) bei der Berechnung der prozentualen Kursveränderungen abzufangen.

#### Um das Projekt sauber aufzusetzen und eine konfliktfreie Umgebung zu garantieren, empfiehlt es sich, diese Abhängigkeiten direkt in einer Datei festzuhalten. Hier ist der exakte, überschneidungsfreie Inhalt für eine requirements.txt:

'''
beautifulsoup4==4.12.3
pandas==2.2.2
requests==2.32.3
yfinance==0.2.40
'''
