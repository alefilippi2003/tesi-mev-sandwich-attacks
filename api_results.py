import os
import pandas as pd
from dune_client.client import DuneClient

# ==========================================
# 1. I TUOI DATI
# ==========================================
DUNE_API_KEY = os.environ["DUNE_API_KEY"]
QUERY_ID = int(os.environ["DUNE_QUERY_ID"])  # ID della query sandwitch_query.sql su Dune

try:
    print(f"Connessione al server API (Query ID: {QUERY_ID})...")
    dune = DuneClient(DUNE_API_KEY)
    
    print("📡 Richiesta dell'intero dataset. Se l'API ha limiti sui 'Datapoints', si bloccherà qui.")
    print("☕ Attendi...")
    
    # Tentiamo di scaricare l'ultimo risultato calcolato
    df = dune.get_latest_result_dataframe(QUERY_ID)
    
    if df.empty:
        print("⚠️ I dati sono vuoti. Forse la query non ha trovato risultati?")
    else:
        # Se arriviamo qui, l'impossibile è successo!
        nome_file = "sandwich_maggio_ECONOMIA.csv"
        df.to_csv(nome_file, index=False)
        
        print("\n==================================================")
        print(f"Totale righe estratte: {len(df):,}")
        print(f"File salvato come: {nome_file}")
        print("==================================================")

except Exception as e:
    print("Dettagli dell'errore restituito dal server Dune:")
    print(e)
