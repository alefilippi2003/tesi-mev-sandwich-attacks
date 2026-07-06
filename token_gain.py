import pandas as pd
import numpy as np

# 1. Funzione matematica per arrotondare a 5 cifre significative
def arrotonda_cifre_significative(x, cifre=5):
    if x == 0 or pd.isna(x):
        return 0
    try:
        return round(x, cifre - int(np.floor(np.log10(abs(x)))) - 1)
    except:
        return 0

# 2. Carica i dati gestendo gli errori (ignora righe corrotte)
df = pd.read_csv('risultati_scambi_token_2026.csv', on_bad_lines='skip')
df['quantita_grezza'] = pd.to_numeric(df['quantita_grezza'], errors='coerce').fillna(0)

# 3. Applica l'arrotondamento preventivo per uccidere il "dust"
df['quantita_approssimata'] = df['quantita_grezza'].apply(lambda x: arrotonda_cifre_significative(x, 5))

# Recuperiamo gli hash front e back per ogni coppia per averli nel report finale
hashes_df = df.groupby('id_coppia').apply(
    lambda g: pd.Series({
        'hash_front': g[g['tipo_run'] == 'Front']['hash'].iloc[0] if len(g[g['tipo_run'] == 'Front']) > 0 else None,
        'hash_back': g[g['tipo_run'] == 'Back']['hash'].iloc[0] if len(g[g['tipo_run'] == 'Back']) > 0 else None
    })
).reset_index()

# 4. Calcola le uscite (Outflows) raggruppate per utente all'interno dello stesso sandwich
outflows = df.groupby(['id_coppia', 'token_contract', 'from'])['quantita_approssimata'].sum().reset_index()
outflows.rename(columns={'from': 'address', 'quantita_approssimata': 'amount_out'}, inplace=True)

# 5. Calcola le entrate (Inflows)
inflows = df.groupby(['id_coppia', 'token_contract', 'to'])['quantita_approssimata'].sum().reset_index()
inflows.rename(columns={'to': 'address', 'quantita_approssimata': 'amount_in'}, inplace=True)

# Unisce In e Out
flows = pd.merge(outflows, inflows, on=['id_coppia', 'token_contract', 'address'], how='outer').fillna(0)

# 6. Differenza netta per scoprire chi ha accumulato il token
flows['differenza'] = flows['amount_in'] - flows['amount_out']

# Eliminiamo scarti infinitesimi dovuti a Python che fa operazioni con i float
flows['differenza'] = flows['differenza'].round(2)

# 7. Regola d'Oro: Escludi se la differenza è 0 (o negativa). Tieni solo i guadagni.
guadagni = flows[flows['differenza'] > 0].copy()

# Uniamo i dati con gli hash estratti prima
risultato_finale = pd.merge(guadagni, hashes_df, on='id_coppia', how='left')

# Rinominiamo le colonne per chiarezza e le riordiniamo
colonne_finali = ['id_coppia', 'hash_front', 'hash_back', 'address', 'token_contract', 'differenza']
risultato_finale = risultato_finale[colonne_finali].rename(columns={
    'address': 'utente_che_ha_guadagnato',
    'token_contract': 'token',
    'differenza': 'quantita_guadagnata'
})

# Salvataggio in ordine di quantità guadagnata
risultato_finale = risultato_finale.sort_values(['quantita_guadagnata'], ascending=False)
risultato_finale.to_csv('guadagni_esatti_sandwich_26.csv', index=False)

print("Calcolo completato! Creato il file guadagni_esatti_sandwich.csv.")
