#!/usr/bin/env python3
"""
calcola_roi.py — Calcolo ROI/payback di un impianto fotovoltaico.

CALCOLO PURO: nessuna chiamata di rete, nessuna dipendenza esterna (solo stdlib).
Tutti i dati (produzione, costi, prezzi, incentivi) arrivano come PARAMETRI:
la skill li raccoglie a monte (es. la produzione reale dal connettore PVGIS) e
li passa qui. Questo script si limita a fare i conti.

⚠️ MATERIALE DIDATTICO — modello semplificato a scopo formativo. Vedi README.

Uso da CLI:
    python3 calcola_roi.py --kwp 160 --prod 1237 --costo-kwp 750 \
        --prezzo-evitato 0.22 --autoconsumo 0.65 --prezzo-immesso 0.08 \
        --degrado 0.005 --incentivo 0.40 --anni 20

Uso come libreria:
    from calcola_roi import calcola
    res = calcola(kwp=160, prod_kwh_kwp=1237, costo_eur_kwp=750, ...)
"""

from __future__ import annotations
import argparse
import json


def calcola(
    kwp: float,
    prod_kwh_kwp: float,
    costo_eur_kwp: float,
    prezzo_evitato_eur_kwh: float,
    quota_autoconsumo: float,
    prezzo_immesso_eur_kwh: float,
    degrado_annuo: float = 0.005,
    incentivo_pct: float = 0.0,
    anni: int = 20,
) -> dict:
    """Calcola investimento, risparmio annuo, payback e cash-flow cumulato.

    Args:
        kwp: potenza installata (kWp)
        prod_kwh_kwp: producibilità specifica (kWh per kWp l'anno) — es. da PVGIS
        costo_eur_kwp: costo chiavi in mano dell'impianto (€/kWp)
        prezzo_evitato_eur_kwh: prezzo dell'energia che NON compri più (€/kWh)
        quota_autoconsumo: frazione di produzione autoconsumata (0..1)
        prezzo_immesso_eur_kwh: prezzo di vendita dell'energia immessa in rete (€/kWh)
        degrado_annuo: calo di resa dei pannelli per anno (es. 0.005 = 0,5%/anno)
        incentivo_pct: quota di investimento coperta da incentivo (0..1)
        anni: orizzonte di calcolo

    Returns:
        dict con investimento_lordo, investimento_netto, produzione_anno1_kwh,
        risparmio_anno1_eur, payback_anni, cashflow_cumulato (lista per anno),
        e i parametri usati.
    """
    if not 0 <= quota_autoconsumo <= 1:
        raise ValueError("quota_autoconsumo deve essere tra 0 e 1")
    if not 0 <= incentivo_pct <= 1:
        raise ValueError("incentivo_pct deve essere tra 0 e 1")

    investimento_lordo = kwp * costo_eur_kwp
    investimento_netto = investimento_lordo * (1 - incentivo_pct)

    produzione_anno1 = kwp * prod_kwh_kwp

    def risparmio_anno(n: int) -> float:
        """Risparmio dell'anno n (1-based), col degrado applicato."""
        fattore_degrado = (1 - degrado_annuo) ** (n - 1)
        prod = produzione_anno1 * fattore_degrado
        autoconsumata = prod * quota_autoconsumo
        immessa = prod * (1 - quota_autoconsumo)
        return (
            autoconsumata * prezzo_evitato_eur_kwh
            + immessa * prezzo_immesso_eur_kwh
        )

    risparmio1 = risparmio_anno(1)

    # cash-flow cumulato: parte da -investimento_netto, somma i risparmi annui
    cashflow = []
    cum = -investimento_netto
    payback = None
    for n in range(1, anni + 1):
        cum += risparmio_anno(n)
        cashflow.append({"anno": n, "cumulato_eur": round(cum, 2)})
        if payback is None and cum >= 0:
            # interpolazione lineare entro l'anno per un payback più preciso
            cum_prec = cashflow[n - 2]["cumulato_eur"] if n >= 2 else -investimento_netto
            quota_anno = cum - cum_prec
            frazione = (-cum_prec / quota_anno) if quota_anno else 0
            payback = round((n - 1) + frazione, 1)

    return {
        "investimento_lordo_eur": round(investimento_lordo, 2),
        "investimento_netto_eur": round(investimento_netto, 2),
        "produzione_anno1_kwh": round(produzione_anno1, 0),
        "risparmio_anno1_eur": round(risparmio1, 2),
        "payback_anni": payback,  # None se non si ripaga entro 'anni'
        "cashflow_cumulato": cashflow,
        "parametri": {
            "kwp": kwp,
            "prod_kwh_kwp": prod_kwh_kwp,
            "costo_eur_kwp": costo_eur_kwp,
            "prezzo_evitato_eur_kwh": prezzo_evitato_eur_kwh,
            "quota_autoconsumo": quota_autoconsumo,
            "prezzo_immesso_eur_kwh": prezzo_immesso_eur_kwh,
            "degrado_annuo": degrado_annuo,
            "incentivo_pct": incentivo_pct,
            "anni": anni,
        },
        "_disclaimer": "Materiale didattico. Modello semplificato, non usare per decisioni reali.",
    }


def _cli():
    p = argparse.ArgumentParser(description="Calcolo ROI fotovoltaico (didattico, calcolo puro)")
    p.add_argument("--kwp", type=float, required=True)
    p.add_argument("--prod", type=float, required=True, help="kWh per kWp l'anno (es. da PVGIS)")
    p.add_argument("--costo-kwp", type=float, required=True, help="€/kWp chiavi in mano")
    p.add_argument("--prezzo-evitato", type=float, required=True, help="€/kWh energia evitata")
    p.add_argument("--autoconsumo", type=float, required=True, help="quota 0..1")
    p.add_argument("--prezzo-immesso", type=float, default=0.08, help="€/kWh vendita")
    p.add_argument("--degrado", type=float, default=0.005, help="frazione/anno")
    p.add_argument("--incentivo", type=float, default=0.0, help="quota 0..1")
    p.add_argument("--anni", type=int, default=20)
    a = p.parse_args()
    res = calcola(
        kwp=a.kwp, prod_kwh_kwp=a.prod, costo_eur_kwp=a.costo_kwp,
        prezzo_evitato_eur_kwh=a.prezzo_evitato, quota_autoconsumo=a.autoconsumo,
        prezzo_immesso_eur_kwh=a.prezzo_immesso, degrado_annuo=a.degrado,
        incentivo_pct=a.incentivo, anni=a.anni,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _cli()
