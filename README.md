# Business-

Repository für Claude Code Integration.

## QuiverQuantitative API Client

TypeScript-Client für die [QuiverQuantitative](https://www.quiverquant.com/) Alternative-Data-API (Congress Trading, Insider Trading, Lobbying u.a.).

### Setup

```bash
npm install
cp .env.example .env   # QUIVER_API_KEY eintragen (siehe https://www.quiverquant.com/api/)
```

### Verwendung

```ts
import { QuiverClient } from "./src/quiverClient.js";

const client = new QuiverClient(); // liest QUIVER_API_KEY aus der Umgebung

// Konkrete Datensätze
await client.getCongressTrading();        // aktuellste Trades, alle Ticker
await client.getCongressTrading("AAPL");   // volle Historie für einen Ticker
await client.getInsiderTrading("AAPL");
await client.getLobbying("AAPL");

// Generischer Zugriff auf beliebige Endpunkte unter /beta
await client.live("govcontracts");
await client.historical("housetrading", "AAPL");
await client.get("/live/wallstreetbets");
```

Beispielskript ausführen: `npm run example` (benötigt gültigen `QUIVER_API_KEY` in `.env`).
