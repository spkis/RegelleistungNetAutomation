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
