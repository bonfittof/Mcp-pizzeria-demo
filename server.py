"""Server MCP remoto per una pizzeria demo, costruito con FastMCP.

Espone i dati (menu, tavoli, prenotazioni) tramite trasporto Streamable
HTTP sull'endpoint /mcp. Tutti i dati sono finti e salvati in data.json:
non c'e' autenticazione, e' pensato solo a scopo dimostrativo.
"""

import json
import os
from pathlib import Path
from threading import Lock

from fastmcp import FastMCP

DATA_PATH = Path(__file__).parent / "data.json"
_lock = Lock()

mcp = FastMCP("Pizzeria Demo")


def _leggi_dati() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _scrivi_dati(dati: dict) -> None:
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)


def _tavoli_occupati(dati: dict, data: str, ora: str) -> set[int]:
    return {
        p["tavolo"]
        for p in dati["prenotazioni"]
        if p["data"] == data and p["ora"] == ora
    }


def _trova_tavoli_liberi(dati: dict, data: str, ora: str, persone: int) -> list[dict]:
    occupati = _tavoli_occupati(dati, data, ora)
    liberi = [
        t for t in dati["tavoli"]
        if t["numero"] not in occupati and t["posti"] >= persone
    ]
    return sorted(liberi, key=lambda t: t["posti"])


@mcp.tool()
def leggi_menu() -> list[dict]:
    """Restituisce l'elenco delle pizze del menu con ingredienti e prezzo."""
    dati = _leggi_dati()
    return dati["menu"]


@mcp.tool()
def verifica_disponibilita(data: str, ora: str, persone: int) -> dict:
    """Verifica se c'e' un tavolo libero per una data, ora e numero di persone.

    Args:
        data: Data della prenotazione nel formato YYYY-MM-DD.
        ora: Ora della prenotazione nel formato HH:MM.
        persone: Numero di persone.
    """
    with _lock:
        dati = _leggi_dati()
        liberi = _trova_tavoli_liberi(dati, data, ora, persone)
    return {
        "disponibile": len(liberi) > 0,
        "tavoli_liberi": liberi,
    }


@mcp.tool()
def crea_prenotazione(nome: str, telefono: str, data: str, ora: str, persone: int) -> dict:
    """Crea una nuova prenotazione assegnando automaticamente un tavolo libero.

    Args:
        nome: Nome del cliente.
        telefono: Numero di telefono del cliente.
        data: Data della prenotazione nel formato YYYY-MM-DD.
        ora: Ora della prenotazione nel formato HH:MM.
        persone: Numero di persone.
    """
    with _lock:
        dati = _leggi_dati()
        liberi = _trova_tavoli_liberi(dati, data, ora, persone)
        if not liberi:
            return {
                "successo": False,
                "messaggio": "Nessun tavolo disponibile per la data, ora e numero di persone richiesti.",
            }

        tavolo = liberi[0]["numero"]
        nuovo_id = max((p["id"] for p in dati["prenotazioni"]), default=0) + 1
        prenotazione = {
            "id": nuovo_id,
            "nome": nome,
            "telefono": telefono,
            "data": data,
            "ora": ora,
            "persone": persone,
            "tavolo": tavolo,
        }
        dati["prenotazioni"].append(prenotazione)
        _scrivi_dati(dati)

    return {
        "successo": True,
        "messaggio": f"Prenotazione confermata al tavolo {tavolo}.",
        "prenotazione": prenotazione,
    }


@mcp.tool()
def lista_prenotazioni(data: str) -> list[dict]:
    """Elenca tutte le prenotazioni per una data specifica.

    Args:
        data: Data nel formato YYYY-MM-DD.
    """
    with _lock:
        dati = _leggi_dati()
    return [p for p in dati["prenotazioni"] if p["data"] == data]


@mcp.tool()
def cancella_prenotazione(id: int) -> dict:
    """Cancella una prenotazione esistente dato il suo id.

    Args:
        id: Identificativo della prenotazione da cancellare.
    """
    with _lock:
        dati = _leggi_dati()
        originarie = dati["prenotazioni"]
        rimanenti = [p for p in originarie if p["id"] != id]
        if len(rimanenti) == len(originarie):
            return {
                "successo": False,
                "messaggio": f"Nessuna prenotazione trovata con id {id}.",
            }
        dati["prenotazioni"] = rimanenti
        _scrivi_dati(dati)

    return {"successo": True, "messaggio": f"Prenotazione {id} cancellata."}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
