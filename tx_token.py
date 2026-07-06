import csv
import time
from web3 import Web3

# ==========================================
# 1. CONFIGURAZIONE
# ==========================================
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/{api_key_alchemy}"
web3 = Web3(Web3.HTTPProvider(alchemy_url))

file_input = 'hash_tx_2026.csv'
file_output = 'risultati_scambi_token_2026.csv' 

# La firma universale (senza lo 0x per sicurezza)
TRANSFER_SIG = "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

if not web3.is_connected():
    print("Errore critico: Impossibile connettersi ad Alchemy.")
    exit()

# ==========================================
# 2. FUNZIONE DI DECODIFICA DEI LOGS
# ==========================================
def estrai_scambi_token(tx_hash, tipo, riga_id, max_tentativi=3):
    for tentativo in range(max_tentativi):
        try:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            scambi = []
            
            for log in receipt['logs']:
                topic0_hex = log['topics'][0].hex().replace('0x', '') if len(log['topics']) > 0 else ""
                
                if len(log['topics']) == 3 and topic0_hex == TRANSFER_SIG:
                    token_address = log['address']
                    from_address = "0x" + log['topics'][1].hex()[-40:]
                    to_address = "0x" + log['topics'][2].hex()[-40:]
                    raw_amount = int(log['data'].hex(), 16)
                    
                    scambi.append({
                        'id_coppia': riga_id,
                        'tipo_run': tipo,
                        'hash': tx_hash,
                        'token_contract': web3.to_checksum_address(token_address),
                        'from': web3.to_checksum_address(from_address),
                        'to': web3.to_checksum_address(to_address),
                        'quantita_grezza': raw_amount
                    })
            return scambi
            
        except Exception as e:
            if '429' in str(e):
                time.sleep(2)
            else:
                print(f"Errore su {tx_hash}: {e}")
                return []
    return []

# ==========================================
# 3. LETTURA E SCRITTURA CONTINUA
# ==========================================
# Il mode='a' (append) assicura che se riavvii lo script, non cancelli i dati già scaricati
with open(file_input, mode='r', encoding='utf-8') as f_in, \
     open(file_output, mode='a', encoding='utf-8', newline='') as f_out: 

    lettore_csv = csv.DictReader(f_in)
    colonne = ['id_coppia', 'tipo_run', 'hash', 'token_contract', 'from', 'to', 'quantita_grezza']
    scrittore_csv = csv.DictWriter(f_out, fieldnames=colonne)
    
    # Scrive l'intestazione solo se il file è appena stato creato (vuoto)
    if f_out.tell() == 0:
        scrittore_csv.writeheader()

    contatore_tx = 0

    for riga_id, riga in enumerate(lettore_csv, start=1):
        
        # Estrae FRONT
        scambi_front = estrai_scambi_token(riga['front_run_hash'], 'Front', riga_id)
        for scambio in scambi_front:
            scrittore_csv.writerow(scambio)

        # Estrae BACK
        scambi_back = estrai_scambi_token(riga['back_run_hash'], 'Back', riga_id)
        for scambio in scambi_back:
            scrittore_csv.writerow(scambio)
            
        contatore_tx += 2

        # Mostra a schermo ogni 100 coppie per non intasarvi il terminale
        if riga_id % 100 == 0:
            print(f"Elaborate {riga_id} coppie... (In corso)")

        time.sleep(0.05)

print(f"\n!!! ESTRAZIONE COMPLETATA !!! Creato il file '{file_output}'.")
