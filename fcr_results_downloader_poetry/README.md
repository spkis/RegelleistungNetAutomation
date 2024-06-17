### README.md

# RegelleistungNetAutomation

## Übersicht

Dieses Projekt automatisiert den Download und die Verarbeitung von Daten zur Regelleistung aus dem FCR-Marktsegment. Die Daten werden täglich heruntergeladen, verarbeitet und in einer CSV-Datei gespeichert, die einfach in eine InfluxDB-Datenbank importiert werden kann.

## Funktionen

- **Automatischer Download der Daten**: Lädt täglich die aktuellen FCR-Daten im Excel-Format von der Regelleistungs.net-Website herunter.
- **Datenverarbeitung**: Konvertiert die heruntergeladenen Daten in ein CSV-Format und strukturiert sie so, dass sie für die Verwendung in einer InfluxDB-Datenbank geeignet sind.
- **Zeitgesteuerte Ausführung**: Führt das Skript täglich zur festgelegten Zeit aus.

## Verzeichnisstruktur

```
regelleistung/
│
├── fcr_results/
│   ├── __init__.py
│   └── fcr_results.py
│
├── main.py
├── pyproject.toml
├── poetry.lock
└── Dockerfile
```

## Anforderungen

- Python 3.x
- [Poetry](https://python-poetry.org/)

## Installation und Ausführung

1. **Projekt herunterladen oder klonen**:
   
   ```ssh
   git clone https://github.com/Richigeht/RegelleistungNetAutomation
   cd RegelleistungNetAutomation
   ```

2. **Abhängigkeiten mit Poetry installieren**:
   
   ```sh
   poetry install
   ```

3. **Hauptskript ausführen**:
   
   Starten Sie das Skript, um den täglichen Download und die Verarbeitung der Daten zu automatisieren.

   ```sh
   poetry run python main.py
   ```

## Docker

Das Projekt kann auch als Docker-Container ausgeführt werden.

1. **Docker-Image bauen**:
   
   ```sh
   docker build -t regelleistungnetautomation .
   ```

2. **Docker-Container starten**:
   
   ```sh
   docker run -d --name regelleistungnetautomation regelleistungnetautomation
   ```

## Konfigurationsoptionen

Das Skript kann so konfiguriert werden, dass es entweder stündliche oder vierstündliche Datenpunkte generiert. Standardmäßig ist die Generierung stündlicher Datenpunkte aktiviert. Um dies zu ändern, passen Sie den `hourly`-Parameter in der `main`-Funktion in `fcr_results.py` an:

```python
df = process_data(file_content, hourly=True)  # Setzen Sie hourly=False, um vierstündliche Daten zu verwenden
```

## Detaillierte Beschreibung der Skripte

### `fcr_results.py`

Dieses Skript enthält die Hauptlogik für den Download und die Verarbeitung der Daten.
```

### Dockerfile

```Dockerfile
# Dockerfile

# Verwenden Sie das offizielle Python-Image als Basis
FROM python:3.12

# Setzen Sie das Arbeitsverzeichnis
WORKDIR /app

# Kopieren Sie die pyproject.toml und poetry.lock Dateien in das Arbeitsverzeichnis
COPY pyproject.toml poetry.lock /app/

# Installieren Sie Poetry
RUN pip install poetry

# Installieren Sie die Abhängigkeiten
RUN poetry install

# Kopieren Sie den Rest des Anwendungscodes in das Arbeitsverzeichnis
COPY . /app

# Definieren Sie den Befehl zum Ausführen des Skripts
CMD ["poetry", "run", "python", "main.py"]
```

### pyproject.toml

Stellen Sie sicher, dass Ihre `pyproject.toml` Datei wie folgt aussieht:

```toml
[tool.poetry]
name = "regelleistungnetautomation"
version = "0.1.0"
description = ""
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
requests = "^2.25.1"
pandas = "^1.2.3"
schedule = "^1.1.0"
openpyxl = "^3.0.7"

[tool.poetry.dev-dependencies]
# Fügen Sie hier Ihre Entwicklungsabhängigkeiten hinzu

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```
