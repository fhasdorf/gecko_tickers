import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from pathlib import Path


def fetch_duesseldorf_ipos():
    url = "https://www.boerse-duesseldorf.de/neueinfuehrungen/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        print("Lade Daten von Börse Düsseldorf...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        name_cells = soup.find_all('td', class_='td-name')

        ipo_news = []

        # Datum von genau heute minus 5 Tage
        limit_datum = datetime.now() - timedelta(days=5)
        print(f"Filter aktiv: Lade nur IPOs ab dem {limit_datum.strftime('%d.%m.%Y')}")

        for cell in name_cells:
            link = cell.find('a')
            if not link:
                continue

            for span in link.find_all('span'):
                span.decompose()

            name = link.text.strip()

            next_td = cell.find_next_sibling('td')

            if next_td:
                for span in next_td.find_all('span'):
                    span.decompose()
                erstnotiz = next_td.text.strip()  # Text, z.B. "23.06.2026"
            else:
                erstnotiz = "Unbekannt"

            # --- DATUMS-FILTER ---
            try:
                ipo_datum = datetime.strptime(erstnotiz, "%d.%m.%Y")
                if ipo_datum < limit_datum:
                    continue
            except ValueError:
                # Falls in der Tabelle mal Quatsch steht (kein echtes Datum),
                # nehmen wir es sicherheitshalber trotzdem auf.
                pass

            ipo_news.append({
                "tag": "IPO",
                "title": f"{name} | ERSTNOTIZ: {erstnotiz}",
                "url": url
            })

        # --- FIX: Pfad relativ zum Script-Ordner (nicht zum cwd) ---
        base_dir = Path(__file__).parent
        output_file = base_dir / "ipo.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(ipo_news, f, ensure_ascii=False, indent=4)

        print(f"ERFOLG: {output_file} mit {len(ipo_news)} aktuellen Einträgen erstellt!")

    except Exception as e:
        print(f"Kritischer Fehler beim Ausführen: {e}")


if __name__ == "__main__":
    fetch_duesseldorf_ipos()
