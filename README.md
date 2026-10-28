# Analisi Quantitativa: MEV e Sandwich Attacks su Ethereum

Questa repository contiene l'intera pipeline di *Data Engineering* sviluppata a supporto del lavoro di Tesi di Laurea. Il codice sorgente illustra l'estrazione, la pulizia e la valorizzazione economica dei dati relativi ai *Sandwich Attacks* sulla blockchain di Ethereum.

## Struttura del Progetto e Pipeline dei Dati

Il flusso di lavoro è suddiviso nei seguenti script, progettati per essere eseguiti in ordine sequenziale:

### Fase 1: Estrazione e Identificazione
* **`sandwitch_query.sql`**: Query eseguita su *Dune Analytics*. Implementa un principio euristico per identificare le sequenze di attacco confrontando i token scambiati e isola le transazioni di *front-run* e *back-run*.
* **`api_results.py`**: Modulo Python per l'estrazione massiva dei dati. Si interfaccia tramite API con i server di Dune per scaricare il dataset base in formato CSV.

### Fase 2: Analisi On-Chain e Riconciliazione (Token Gain)
* **`tx_token.py`**: Script di estrazione profonda. Interroga direttamente i nodi Ethereum tramite RPC (provider Alchemy) e `Web3.py`. Decodifica i *transaction receipts* per isolare gli eventi ERC-20 `Transfer`, estraendo le quantità grezze scambiate per ogni attacco.
* **`token_gain.py`**: Script di bilanciamento. Aggrega i log di trasferimento in flussi di cassa (Inflows/Outflows). Implementa una funzione matematica infallibile per arrotondare le cifre significative, eliminando il *dust* crittografico, per poi calcolare il profitto lordo netto in WETH.

### Fase 3: Elaborazione dei Costi Operativi (Gas Fee)
* **`gas_tx.py`**: Esegue il *data cleaning* strutturale del dataset. Riassegna e separa correttamente gli attributi di costo (gas utilizzato e prezzo del gas) tra *front-run* e *back-run*, calcolando la tariffa di transazione lorda in Gwei.

### Fase 4: Valorizzazione Fiat (Conversione in Dollari)
* **`weth_to_usd.py`**: Scarica le serie storiche dei prezzi (ETH-USD) tramite la libreria `yfinance`. Esegue una mappatura cronologica con interpolazione dei dati mancanti e converte i profitti lordi da frazioni di *Wei* a Dollari Statunitensi.
* **`usd_fee.py`**: Applica la medesima architettura di valorizzazione storica ai costi operativi, convertendo le commissioni di rete da Gwei a Dollari (USD).

### Fase 5: Consolidamento Finale
* **`gain_usd.py`**: Ultimo modulo della pipeline. Attraverso operazioni di *Left Join*, ricongiunge i profitti in USD con i rispettivi costi di *front-run* e *back-run*. Gestisce la normalizzazione dei valori mancanti e calcola il differenziale definitivo (*Net Gain*).

## Esecuzione

Richiede Python 3.10+ e un account [Dune](https://dune.com) e [Alchemy](https://www.alchemy.com).

```bash
pip install -r requirements.txt
export DUNE_API_KEY=...       # chiave API Dune
export DUNE_QUERY_ID=...      # ID della query sandwitch_query.sql salvata su Dune
export ALCHEMY_API_KEY=...    # chiave API Alchemy (Ethereum mainnet)

python api_results.py   # Fase 1
python tx_token.py      # Fase 2
python token_gain.py
python gas_tx.py        # Fase 3
python weth_to_usd.py   # Fase 4
python usd_fee.py
python gain_usd.py      # Fase 5
```

I CSV intermedi e finali non sono inclusi nella repository.

## Licenza

MIT
