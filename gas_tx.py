import pandas as pd

# 1. Carica il tuo dataset (sostituisci 'il_tuo_file.csv' con il percorso del tuo file)
df = pd.read_csv('ECONOMIA_apr_mag_26.csv')

# 2. Creiamo il DataFrame per le transazioni "FRONT"
# (Visto che sono invertiti, prendiamo i dati dalle colonne "back_")
df_front = df[['block_number', 'block_time', 'attacker_address', 'back_run_hash', 'back_gas_used', 'back_gas_price_gwei']].copy()
df_front['type'] = 'front'  # Assegniamo il tipo corretto
df_front.rename(columns={
    'back_run_hash': 'hash',
    'back_gas_used': 'gas_used',
    'back_gas_price_gwei': 'gas_price'
}, inplace=True)

# 3. Creiamo il DataFrame per le transazioni "BACK"
# (Prendiamo i dati dalle colonne "front_")
df_back = df[['block_number', 'block_time', 'attacker_address', 'front_run_hash', 'front_gas_used', 'front_gas_price_gwei']].copy()
df_back['type'] = 'back'  # Assegniamo il tipo corretto
df_back.rename(columns={
    'front_run_hash': 'hash',
    'front_gas_used': 'gas_used',
    'front_gas_price_gwei': 'gas_price'
}, inplace=True)

# 4. Uniamo i due DataFrame
df_final = pd.concat([df_front, df_back], ignore_index=True)
# ---> ECCO LA NUOVA RIGA <---
df_final['transaction_fee'] = df_final['gas_used'] * df_final['gas_price']

# 5. Riordiniamo le colonne includendo anche la nuova
colonne_ordinate = [
    'block_number', 
    'block_time', 
    'attacker_address', 
    'type', 
    'hash', 
    'gas_used', 
    'gas_price',
    'transaction_fee'  # Nuova colonna alla fine
]
df_final = df_final[colonne_ordinate]

# Opzionale: Ordiniamo i dati per numero di blocco per mantenere i front/back vicini
df_final.sort_values(by=['block_number', 'type'], ascending=[True, False], inplace=True)
df_pulito = df_final.drop_duplicates(keep='first')
# 6. Salviamo il risultato in un nuovo file CSV
df_pulito.to_csv('gas_front_back_26.csv', index=False)

print("Trasformazione completata! File salvato come 'dataset_modellato.csv'")