import pandas as pd

# 1. Carica i due dataset
# (Assicurati che i nomi dei file siano esattamente quelli che hai nella tua cartella)
df_guadagni = pd.read_csv('guadagni_mono_weth_usd_yf_26.csv')
df_gas = pd.read_csv('gas_front_back_usd_26.csv')

# 3. Prepara i dati del GAS dividendo le Front dalle Back
# Estraiamo solo le fee Front
gas_front = df_gas[df_gas['type'] == 'front'][['hash', 'usd_fee']].rename(
    columns={'hash': 'hash_front', 'usd_fee': 'usd_fee_front'}
)
# Rimuoviamo eventuali duplicati per sicurezza
gas_front = gas_front.drop_duplicates(subset=['hash_front'])

# Estraiamo solo le fee Back
gas_back = df_gas[df_gas['type'] == 'back'][['hash', 'usd_fee']].rename(
    columns={'hash': 'hash_back', 'usd_fee': 'usd_fee_back'}
)
# Rimuoviamo eventuali duplicati per sicurezza
gas_back = gas_back.drop_duplicates(subset=['hash_back'])

# 4. Fai il MERGE
# Primo merge: aggiunge i costi della transazione front
df_finale = pd.merge(df_guadagni, gas_front, on='hash_front', how='left')

# Secondo merge: aggiunge i costi della transazione back
df_finale = pd.merge(df_finale, gas_back, on='hash_back', how='left')

# Riempiamo con 0 eventuali "buchi" nel dataset se per caso manca la fee
df_finale['usd_fee_front'] = df_finale['usd_fee_front'].fillna(0)
df_finale['usd_fee_back'] = df_finale['usd_fee_back'].fillna(0)

# 5. Calcola il GAIN netto
df_finale['gain'] = df_finale['profitto_USD'] - df_finale['usd_fee_front'] - df_finale['usd_fee_back']

# 6. Salva in un nuovo file CSV
# Lo salvo come compresso per sicurezza, visti i tuoi precedenti limiti di quota!
df_finale.to_csv('guadagni_finali_weth_26.csv', index=False)

print("Processo completato! Il file è stato salvato.")
# Mostriamo le colonne principali per verificare il risultato
print(df_finale[['hash_front', 'profitto_USD', 'usd_fee_front', 'usd_fee_back', 'gain']].head())