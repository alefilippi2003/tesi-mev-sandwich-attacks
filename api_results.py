import pandas as pd
from dune_client.client import DuneClient

print("==================================================")
print("🚀 TEST ESTREMO: Estrazione massiva via API Dune")
print("==================================================")

# ==========================================
# 1. I TUOI DATI
# ==========================================
# Inserisci qui la tua API Key e il Query ID di Gennaio 2024
DUNE_API_KEY = "{api_key_dune}"
QUERY_ID = 7722571  # Sostituisci con il tuo Query ID

try:
    print(f"⏳ Connessione al server API (Query ID: {QUERY_ID})...")
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
        print(f"📊 Totale righe estratte: {len(df):,}")
        print(f"💾 File salvato come: {nome_file}")
        print("==================================================")

except Exception as e:
    print("\n==================================================")
    print("❌ IL MURO A PAGAMENTO HA COLPITO.")
    print("==================================================")
    print("Dettagli dell'errore restituito dal server Dune:")
    print(e)
    print("\n👉 Questo conferma che per estrazioni massive serve l'abbonamento da 350€.")
    print("👉 Il prossimo passo logico è usare il 'Metodo del Campione' da 1.000 righe.")