import pandas as pd
import yfinance as yf

# 1. Carica il dataset 
# (Se hai salvato il file compresso come ti ho suggerito prima, usa questo:)
df = pd.read_csv('gas_front_back_26.csv')
# (Altrimenti, se hai risolto lo spazio e salvato normalmente, de-commenta la riga sotto:)
# df = pd.read_csv('gas_front_back.csv')

# 2. Crea una colonna temporanea estraendo solo la Data (senza orario e timezone)
df['date'] = pd.to_datetime(df['block_time']).dt.date

# 3. Trova la data minima e massima per dire a yfinance che periodo scaricare
start_date = df['date'].min()
# Aggiungiamo un giorno alla data di fine, perché yfinance esclude il giorno finale
end_date = df['date'].max() + pd.Timedelta(days=1)

print(f"Scaricando i prezzi storici di ETH-USD dal {start_date} al {end_date}...")

# 4. Scarica i dati di Ethereum (Ticker: ETH-USD)
eth_data = yf.download('ETH-USD', start=start_date, end=end_date)

# Prendiamo solo i prezzi di chiusura ("Close"). 
# Gestiamo le varie versioni della libreria yfinance:
if isinstance(eth_data.columns, pd.MultiIndex):
    eth_prices = eth_data['Close']['ETH-USD']
else:
    eth_prices = eth_data['Close']

# Creiamo un dizionario {data: prezzo_in_usd}
price_dict = {index.date(): price for index, price in eth_prices.items()}

# 5. Mappiamo il prezzo in USD per ogni riga in base alla data del blocco
df['eth_price_usd'] = df['date'].map(price_dict)

# 6. Calcoliamo la fee in USD! (transaction_fee * 10^-9 * prezzo_ETH)
df['usd_fee'] = df['transaction_fee'] * (10**-9) * df['eth_price_usd']

# 7. Facciamo un po' di pulizia eliminando la colonna temporanea 'date'
df.drop(columns=['date'], inplace=True)

# 8. Salviamo il nuovo dataset aggiornato (sempre compresso per evitare l'Errore 122 del disco!)
df.to_csv('gas_front_back_usd_26.csv', index=False)

print("Operazione completata con successo!")
# Mostriamo un'anteprima per verificare i calcoli
print(df[['block_time', 'transaction_fee', 'eth_price_usd', 'usd_fee']].head())