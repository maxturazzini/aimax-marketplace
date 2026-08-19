# valutazione-fv

Plugin Claude Code per la **valutazione di fattibilità di un impianto fotovoltaico** sul tetto di una sede aziendale. Dato un rilievo del tetto e le coordinate, stima i mq netti sfruttabili, recupera la **produzione reale via PVGIS** (connettore MCP), calcola **payback e cash-flow** con uno script di calcolo, e produce una scheda di sintesi per un comitato. Pensato per essere applicato in serie a più sedi.

> ## ⚠️ Materiale didattico — non usare per decisioni reali
> Questo plugin nasce come **esempio formativo** dei workshop **AI, MAX**. Mostra come una valutazione si trasforma in un metodo riutilizzabile (skill + script + connettore MCP).
>
> **I numeri non sono affidabili per decisioni di investimento:**
> - Il modello di calcolo (`calcola_roi.py`) è **semplificato** a scopo didattico.
> - Gli **incentivi** e i **costi €/kWp** cambiano nel tempo: vanno verificati con fonti aggiornate, non dati per buoni.
> - La stima dei mq netti e del dimensionamento è **indicativa**.
> - Per una valutazione vera serve un **progettista qualificato** e un sopralluogo.
>
> Usalo per **imparare il metodo**, non per decidere se mettere il fotovoltaico.

## Cosa contiene

```
valutazione-fv/
├── .claude-plugin/plugin.json   metadati del plugin
├── .mcp.json                     referenzia il connettore PVGIS (server remoto)
├── skills/valutazione-fv-sede/
│   ├── SKILL.md                  il metodo (stima → PVGIS → calcolo → scheda)
│   └── scripts/calcola_roi.py    calcolo ROI/payback — PURO, nessuna chiamata di rete
├── LICENSE                       CC BY-NC 4.0 — © Max Turazzini
└── README.md
```

## Installazione (Claude Code)

```
/plugin marketplace add maxturazzini/aimax-marketplace
/plugin install valutazione-fv
```

All'attivazione, Claude Code propone di collegare anche il **connettore PVGIS** dichiarato in `.mcp.json` (server pubblico remoto): conferma quando richiesto. Da quel momento la skill può recuperare la produzione reale di un tetto date le coordinate.

> Su **Claude.ai (web)** il plugin si installa dalla directory plugin del marketplace AI, MAX (Personalizza → Plugin). Se il connettore PVGIS non risulta già collegato col plugin, aggiungilo a mano come "Connettore personalizzato" con URL `https://pvgis-mcp.k76js8pfvm.workers.dev/mcp`.

## Il connettore PVGIS

PVGIS è il servizio ufficiale della Commissione Europea (JRC) per la producibilità fotovoltaica. Il connettore è un MCP server (Cloudflare Worker) pubblico: codice e dettagli in **[github.com/maxturazzini/pvgis-mcp](https://github.com/maxturazzini/pvgis-mcp)**. API PVGIS gratuita, senza chiave.

## Lo script di calcolo

`calcola_roi.py` fa **solo calcolo** (stdlib, zero rete). Esempio:
```
python3 scripts/calcola_roi.py --kwp 160 --prod 1237 --costo-kwp 750 \
  --prezzo-evitato 0.22 --autoconsumo 0.65 --prezzo-immesso 0.08 \
  --degrado 0.005 --incentivo 0.40 --anni 20
```
La produzione (`--prod`, kWh/kWp) la fornisce la skill recuperandola da PVGIS; lo script non la calcola né la scarica.

## Licenza

[CC BY-NC 4.0](./LICENSE) — © Max Turazzini. Puoi usarlo e adattarlo citando l'autore; **non** per scopi commerciali.
