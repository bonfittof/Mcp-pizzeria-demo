# MCP Pizzeria Demo

Server MCP (Model Context Protocol) remoto per una pizzeria demo, scritto in
Python con [FastMCP](https://gofastmcp.com/). Espone menu, tavoli e
prenotazioni finte tramite trasporto **Streamable HTTP** sull'endpoint
`/mcp`.

> Demo a scopo dimostrativo/didattico: i dati sono finti, salvati in un
> semplice file `data.json`, e **non c'e' alcuna autenticazione**. Non
> usare in produzione con dati reali.

## Funzionalita' (tool MCP)

- `leggi_menu()` — restituisce l'elenco delle 10 pizze del menu con
  ingredienti e prezzo.
- `verifica_disponibilita(data, ora, persone)` — controlla se c'e' un
  tavolo libero per la data (`YYYY-MM-DD`), l'ora (`HH:MM`) e il numero di
  persone richiesti.
- `crea_prenotazione(nome, telefono, data, ora, persone)` — crea una nuova
  prenotazione assegnando automaticamente il tavolo libero piu' piccolo
  disponibile.
- `lista_prenotazioni(data)` — elenca tutte le prenotazioni per una data.
- `cancella_prenotazione(id)` — cancella una prenotazione dato il suo id.

I dati (menu, 8 tavoli da 2/4/6 posti e alcune prenotazioni di esempio)
sono definiti in [`data.json`](./data.json) e vengono letti/scritti dal
server ad ogni chiamata.

## Struttura del progetto

```
.
├── server.py         # Server MCP (FastMCP, trasporto Streamable HTTP)
├── data.json          # Dati demo: menu, tavoli, prenotazioni
├── requirements.txt   # Dipendenze Python
├── render.yaml         # Configurazione per il deploy su Render
└── README.md
```

## Esecuzione in locale

Requisiti: Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python server.py
```

Il server si mette in ascolto su `http://0.0.0.0:8000/mcp` (la porta puo'
essere cambiata impostando la variabile d'ambiente `PORT`).

Per collegare un client MCP (es. Claude, un'app compatibile MCP, o
`mcp-cli`) usa l'URL dell'endpoint Streamable HTTP:

```
http://localhost:8000/mcp
```

## Deploy su Render

Il repository include un file [`render.yaml`](./render.yaml) che descrive
il servizio come Blueprint di Render, cosi' il deploy richiede pochi passi.

1. **Crea un account su [Render](https://render.com/)** (se non lo hai
   gia').
2. **Fai il push del repository su GitHub** (o un altro provider Git
   supportato).
3. Su Render, vai su **New > Blueprint** e collega il repository.
4. Render trovera' automaticamente `render.yaml` e configurera' un
   servizio web Python chiamato `mcp-pizzeria-demo`:
   - `buildCommand`: `pip install -r requirements.txt`
   - `startCommand`: `python server.py`
   - la porta viene letta dalla variabile d'ambiente `PORT`, impostata
     automaticamente da Render.
5. Clicca su **Apply/Create** per avviare il deploy.
6. A deploy completato, Render fornisce un URL pubblico del tipo
   `https://mcp-pizzeria-demo.onrender.com`. L'endpoint MCP sara'
   disponibile su:

   ```
   https://mcp-pizzeria-demo.onrender.com/mcp
   ```

### Deploy manuale (senza Blueprint)

In alternativa, puoi creare il servizio manualmente dalla dashboard di
Render:

1. **New > Web Service**, collega il repository.
2. **Runtime**: Python 3.
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python server.py`
5. Non serve impostare manualmente `PORT`: Render la fornisce
   automaticamente e il server la legge da `os.environ["PORT"]`.

## Note

- Non essendoci autenticazione, chiunque conosca l'URL pubblico puo'
  leggere il menu e creare/cancellare prenotazioni: e' voluto, trattandosi
  di una demo con dati finti.
- Il file `data.json` viene modificato direttamente sul filesystem del
  servizio: su Render il filesystem dei servizi web free e' **effimero**
  (viene ripristinato ad ogni nuovo deploy o riavvio), quindi le
  prenotazioni create tramite il server in produzione non sono
  persistenti a lungo termine. Per un uso reale servirebbe un database o
  un disco persistente.
