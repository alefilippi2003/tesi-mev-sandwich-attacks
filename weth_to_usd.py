import pandas as pd
import yfinance as yf

# 1. Carica il dataset dei guadagni WETH
df = pd.read_csv('guadagni_sandwich_26_eth_date.csv')

# 2. Crea una colonna temporanea estraendo solo la Data
df['date'] = pd.to_datetime(df['block_time']).dt.date

# 3. Trova la data minima e massima per yfinance
start_date = df['date'].min()
# Aggiungiamo un giorno alla data di fine, perché yfinance esclude il giorno finale
end_date = df['date'].max() + pd.Timedelta(days=1)

print(f"Scaricando i prezzi storici di ETH-USD (WETH) dal {start_date} al {end_date} tramite yfinance...")

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
df['weth_price_usd'] = df['date'].map(price_dict)

# Gestiamo eventuali buchi nei dati di yfinance (forward e backward fill)
df.sort_values('block_time', inplace=True)
df['weth_price_usd'] = df['weth_price_usd'].ffill().bfill()

# 6. Calcoliamo il guadagno in USD! 
# Ricorda: i dati sono in Wei (18 decimali), quindi moltiplichiamo per 10^-18
df['profitto_USD'] = df['quantita_guadagnata'] * (10**-18) * df['weth_price_usd']

# 7. Pulizia: eliminiamo la colonna temporanea 'date'
df.drop(columns=['date'], inplace=True)

# 8. Salviamo il nuovo dataset aggiornato e compresso
output_file = 'guadagni_mono_weth_usd_yf_26.csv'
df.to_csv(output_file, index=False)

print(f"Operazione completata con successo! File salvato come: {output_file}")
# Mostriamo un'anteprima per verificare i calcoli
print("\nAnteprima risultati:")
print(df[['block_time', 'quantita_guadagnata', 'weth_price_usd', 'profitto_USD']].head())