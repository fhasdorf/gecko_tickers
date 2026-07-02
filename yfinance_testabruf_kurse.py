import yfinance as yf

ticker = yf.Ticker("9AUA.DU")
info = ticker.info

print("=== LIVE-INSPEKTION: THE NEW MEAT CO ===")
print("1. fast_info 'last_price':", ticker.fast_info.get('last_price'))
print("2. info 'currentPrice':   ", info.get('currentPrice'))
print("3. info 'regularMarketPrice':", info.get('regularMarketPrice'))
print("4. info 'bid':            ", info.get('bid'))
print("5. info 'ask':            ", info.get('ask'))
print("6. info 'previousClose':  ", info.get('previousClose'))