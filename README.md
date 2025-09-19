# Clockodo MCP Server

Ein Model Context Protocol (MCP) Server f�r die Integration der Clockodo API mit Claude Desktop. Erm�glicht es Claude, Zeitbuchungen zu verwalten und Arbeitszeiten �ber nat�rliche Sprache zu verfolgen.

## Features

### Tools (Aktionen)
- **Zeiterfassung starten**: Beginne die Zeiterfassung f�r Kunde/Projekt
- **Zeiterfassung stoppen**: Beende die aktuelle Zeiterfassung
- **Zeitbuchung erstellen**: Erstelle manuelle Zeiteintr�ge
- **Laufende Zeiterfassung abrufen**: Zeige aktuell laufende Zeiterfassung
- **Arbeitszeit-Zusammenfassung**: Erhalte �bersicht �ber gearbeitete Stunden

### Resources (Daten)
- **Zeiteintr�ge**: Abrufen von Zeiteintr�gen f�r verschiedene Zeitr�ume
- **Kunden**: Liste aller Kunden
- **Projekte**: Projekte eines bestimmten Kunden
- **Leistungen**: Verf�gbare Leistungskategorien

## Installation

1. **Dependencies installieren**:
   ```bash
   uv sync
   ```

2. **Umgebungsvariablen konfigurieren**:
   ```bash
   cp .env.example .env
   # Bearbeite .env mit deinen Clockodo-Zugangsdaten
   ```

3. **Clockodo API-Zugangsdaten**:
   - Email-Adresse: Deine Clockodo-Login-Email
   - API-Key: Findest du in Clockodo unter "Pers�nliche Daten"

## Verwendung

### Entwicklungsmodus
```bash
uv run mcp dev main.py
```

### Claude Desktop Installation
```bash
uv run mcp install main.py --name "Clockodo Time Tracker"
```

### Mit Environment-Variablen
```bash
uv run mcp install main.py -f .env
```

### Server-Verwaltung

**Server starten**:
```bash
uv run python main.py
```

**Server neu starten**:
```bash
# Aktuellen Server stoppen
pkill -f "python.*main.py"

# Neuen Server starten
uv run python main.py
```

**Server-Status prüfen**:
```bash
ps aux | grep "python.*main.py"
```

**Nach Code-Änderungen**: Nach Änderungen am Code muss der MCP-Server neu gestartet werden, damit die Änderungen wirksam werden.

## Beispiele f�r Claude-Befehle

- "Starte Zeiterfassung f�r Kunde M�ller"
- "Stoppe die Zeiterfassung"
- "Erstelle eine Buchung f�r 3 Stunden Entwicklung gestern"
- "Wie viele Stunden habe ich diese Woche gearbeitet?"
- "Zeige mir alle Projekte von Kunde Schmidt"
- "Was l�uft gerade in der Zeiterfassung?"

## API-Funktionen

### Tools
- `start_time_tracking(customer_name, project_name?, service_name?, description?)`
- `stop_time_tracking()`
- `get_running_entry()`
- `create_time_entry(customer_name, date, start_time, end_time, ...)`
- `get_work_summary(period?)`

### Resources
- `entries://today|yesterday|week|month` - Zeiteintr�ge f�r Zeitraum
- `customers://all` - Alle Kunden
- `projects://{customer_name}` - Projekte eines Kunden
- `services://all` - Alle Leistungen
- `users://all` - Alle Nutzer mit Details

## Technische Details

- **Framework**: FastMCP (Python)
- **API Client**: Async HTTP mit httpx
- **Authentifizierung**: Clockodo API Headers
- **Transport**: STDIO f�r Claude Desktop

## Konfiguration

Die Clockodo API-Zugangsdaten werden �ber Umgebungsvariablen konfiguriert:

```env
CLOCKODO_EMAIL=deine-email@example.com
CLOCKODO_API_KEY=dein-api-key
```

## Fehlerbehandlung

Der Server behandelt verschiedene Fehlertypen:
- API-Authentifizierungsfehler
- Netzwerkverbindungsprobleme
- Ung�ltige Eingabedaten
- Clockodo API-Limits

Alle Fehler werden mit benutzerfreundlichen Nachrichten zur�ckgegeben.