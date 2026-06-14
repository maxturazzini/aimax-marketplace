---
name: valutazione-fv-sede
description: Valuta la fattibilità di un impianto fotovoltaico sul tetto di una sede aziendale e produce una scheda di sintesi per un comitato. Stima i mq netti sfruttabili da un rilievo, recupera la produzione reale via il connettore PVGIS, calcola payback e cash-flow con uno script di calcolo incluso, e genera la scheda a una pagina. Pensata per essere applicata in serie a più sedi. Use this skill when the user wants to evaluate rooftop solar PV on a building, estimate payback/ROI of a photovoltaic system, or standardize a feasibility assessment across multiple sites. Trigger - "valuta fotovoltaico sede", "studio fattibilità FV", "payback impianto fotovoltaico", "/valutazione-fv-sede". MATERIALE DIDATTICO, non per decisioni reali (vedi README).
---

# Valutazione FV sede

Trasforma la valutazione di un impianto fotovoltaico da lavoro artigianale a **metodo ripetibile**: stessa procedura per la prima sede e per le successive.

> ⚠️ **Materiale didattico.** Modello semplificato a scopo formativo (workshop AI, MAX). NON usare per decisioni reali di investimento: i calcoli sono indicativi, gli incentivi cambiano, serve sempre un progettista qualificato. Vedi README del plugin.

## When to use this skill

- Valutare se conviene installare il fotovoltaico sul tetto di una sede
- Stimare payback / ritorno dell'investimento di un impianto FV
- Ripetere la stessa valutazione su più sedi con criteri coerenti
- Preparare una scheda di sintesi FV per un comitato/direzione

## Cosa serve (input)

- **Sede**: indirizzo o coordinate (lat/lon). Se hai un **rilievo del tetto** (PDF/planimetria), allegalo.
- **Obiettivo**: tipicamente autoconsumo (l'azienda consuma di giorno).
- (Opzionale) consumo annuo dell'azienda e quota diurna, per affinare l'autoconsumo.

## Workflow

### 1. Stima la superficie netta sfruttabile
Se c'è un rilievo del tetto, leggilo ed estrai: superficie per falda, esposizione, inclinazione, ostacoli (lucernari, camini, UTA, fasce di rispetto). Ricava i **mq NETTI realmente sfruttabili** (di norma solo la falda esposta a Sud, al netto di ostacoli e di un packing factor ~0,80). Mostra il ragionamento, non solo il numero. Se non c'è rilievo, chiedi i mq di tetto disponibili e applica le stesse decurtazioni in forma prudenziale.

### 2. Dimensiona l'impianto
Dai mq netti stima i **kWp installabili** (regola del pollice ~5-7 mq/kWp con pannelli attuali). Indica un range, non un valore secco.

### 3. Recupera la produzione reale via PVGIS  ⭐
Usa il **connettore PVGIS** (tool `pv_production`) con le coordinate della sede, i kWp stimati, l'inclinazione e l'esposizione della falda buona (aspect 0 = Sud). Ottieni la **produzione reale** (kWh/anno e kWh/kWp) per QUEL tetto specifico — non una stima generica.
- Se il connettore PVGIS non è disponibile, chiedi all'utente di aggiungerlo (vedi README) oppure usa una stima dichiarata (1.100-1.250 kWh/kWp al Nord, 1.250-1.400 Centro, 1.400-1.600 Sud) segnalando che è una stima e non il dato reale.

### 4. Calcola payback e cash-flow
Esegui lo script di calcolo incluso (calcolo puro, nessuna rete):
```
python3 scripts/calcola_roi.py --kwp <KWP> --prod <KWH_PER_KWP_DA_PVGIS> \
  --costo-kwp <EUR_KWP> --prezzo-evitato <EUR_KWH> --autoconsumo <0..1> \
  --prezzo-immesso <EUR_KWH> --degrado 0.005 --incentivo <0..1> --anni 20
```
Lo script restituisce investimento (lordo/netto), risparmio annuo, **payback** e cash-flow cumulato a 20 anni (col degrado pannelli). I costi €/kWp e gli incentivi vigenti vanno recuperati con ricerca web aggiornata (non a memoria: cambiano).

### 5. Produci la scheda per il comitato
Una pagina con: i 4 numeri chiave (kWp, investimento, risparmio annuo, payback), una riga sul contributo all'autonomia energetica, e le assunzioni dichiarate. Segnala sempre i margini di incertezza.

## Applicare alle altre sedi
Ripeti dal punto 1 per ogni sede: cambiano coordinate (→ PVGIS dà la produzione di quel tetto) e geometria del rilievo. Il metodo e lo script restano identici. È questo che rende la valutazione uno **standard**, non un lavoro una-tantum.

## Note
- Lo **script di calcolo** non chiama nulla in rete: i dati entrano come parametri. La parte "dato reale" (produzione) arriva dal connettore PVGIS, gestito dalla skill.
- Il connettore PVGIS è referenziato in `.mcp.json` del plugin (server pubblico, vedi README).
