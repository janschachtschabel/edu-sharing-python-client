## Installieren

Die Bibliothek benötigt **Python 3.11 oder neuer**.

Das Paket ist derzeit **noch nicht auf PyPI veröffentlicht**. Es wird deshalb direkt aus dem Git-Repository installiert.

Es gibt zwei unterstützte Installationswege:

- **pip** – gehört zu einer normalen Python-Installation und ist für den Einstieg meist der einfachste Weg.
- **uv** – ein schneller Python-Paket- und Projektmanager, der sich besonders für Entwicklung und reproduzierbare Umgebungen eignet.

Für normale Anwendungen empfiehlt sich außerdem eine **virtuelle Python-Umgebung (`venv`)**. Dadurch bleiben der edu-sharing Python Client und seine Abhängigkeiten von anderen Python-Projekten getrennt.

### Voraussetzungen

Benötigt werden:

- Python 3.11 oder neuer
- Git
- pip oder uv

Die installierte Python-Version prüfen:

```bash
python --version
```

Beispiel:

```text
Python 3.12.10
```

Unter Windows kann alternativ der Python Launcher verwendet werden:

```powershell
py --version
```

Git prüfen:

```bash
git --version
```

Beispiel:

```text
git version 2.51.0.windows.1
```

Falls Python oder Git noch fehlen:

- Python: https://www.python.org/downloads/
- Git: https://git-scm.com/downloads

---

### Windows: Installation mit pip

Die folgenden Befehle sind für **PowerShell** gedacht.

Zuerst einen Projektordner anlegen:

```powershell
mkdir C:\dev\edu-sharing-test
cd C:\dev\edu-sharing-test
```

Eine virtuelle Python-Umgebung erstellen:

```powershell
python -m venv .venv
```

Falls unter Windows `python` nicht gefunden wird, funktioniert häufig stattdessen:

```powershell
py -m venv .venv
```

Die Umgebung aktivieren:

```powershell
.\.venv\Scripts\Activate.ps1
```

Danach sollte der PowerShell-Prompt ungefähr so aussehen:

```text
(.venv) PS C:\dev\edu-sharing-test>
```

Falls PowerShell die Ausführung von `Activate.ps1` verweigert, kann die Ausführungsrichtlinie nur für die aktuelle PowerShell-Sitzung angepasst werden:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Danach erneut:

```powershell
.\.venv\Scripts\Activate.ps1
```

Optional pip aktualisieren:

```powershell
python -m pip install --upgrade pip
```

Jetzt den aktuellen Stand des edu-sharing Python Clients aus dem `main`-Branch installieren:

```powershell
python -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

Die benötigten Laufzeit-Abhängigkeiten, darunter `httpx` und `attrs`, werden automatisch mitinstalliert.

---

### Windows: Installation mit uv

Wer bereits `uv` verwendet, kann dieselbe Bibliothek mit `uv` installieren.

Zuerst einen Projektordner anlegen:

```powershell
mkdir C:\dev\edu-sharing-test
cd C:\dev\edu-sharing-test
```

Eine virtuelle Umgebung erstellen:

```powershell
uv venv
```

Unter Windows aktivieren:

```powershell
.\.venv\Scripts\Activate.ps1
```

Dann installieren:

```powershell
uv pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

Damit führen `pip` und `uv` zur gleichen Bibliothek; nur das Werkzeug zur Verwaltung der Python-Umgebung und Pakete unterscheidet sich.

---

### Linux und macOS: Installation mit pip

Projektordner anlegen:

```bash
mkdir -p ~/edu-sharing-test
cd ~/edu-sharing-test
```

Virtuelle Umgebung erstellen:

```bash
python3 -m venv .venv
```

Aktivieren:

```bash
source .venv/bin/activate
```

pip aktualisieren:

```bash
python -m pip install --upgrade pip
```

Client installieren:

```bash
python -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

---

### Linux und macOS: Installation mit uv

```bash
mkdir -p ~/edu-sharing-test
cd ~/edu-sharing-test

uv venv
source .venv/bin/activate

uv pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

---

### Installation prüfen

Nach der Installation lässt sich direkt testen, ob Python die Bibliothek findet.

Mit pip oder uv innerhalb der aktivierten Umgebung:

```bash
python -c "from edusharing import Repository; print('edu-sharing Python Client erfolgreich installiert')"
```

Die Ausgabe sollte sein:

```text
edu-sharing Python Client erfolgreich installiert
```

Damit ist zunächst nur geprüft, dass das Paket korrekt installiert wurde. Im nächsten Schritt kann die Verbindung zu einem echten edu-sharing-Repositorium getestet werden.

---

### Verbindung gegen die Staging-Instanz testen

Für einen einfachen lesenden Test kann die öffentliche Staging-Instanz verwendet werden:

```text
https://repository.staging.openeduhub.net
```

Für diesen Test werden **keine Zugangsdaten** benötigt.

Im Projektordner eine Datei `test_connection.py` anlegen:

```python
from edusharing import Repository


REPOSITORY_URL = "https://repository.staging.openeduhub.net"


with Repository(REPOSITORY_URL) as repo:
    about = repo.about()
    who = repo.whoami()

    print("Verbindung erfolgreich")
    print("Repository-Version:", about.repository_version)
    print("Plugins:", about.plugins)
    print("Aktueller Benutzer:", who.authority)
```

Anschließend ausführen:

```bash
python test_connection.py
```

Eine erfolgreiche Verbindung liefert beispielsweise:

```text
Verbindung erfolgreich
Repository-Version: 11.0
Plugins: [...]
Aktueller Benutzer: esguest
```

`esguest` bedeutet, dass der Zugriff anonym erfolgt.

Mit diesem Test werden mehrere Dinge gleichzeitig geprüft:

1. Python findet das installierte `edusharing`-Paket.
2. Der Client kann eine HTTPS-Verbindung herstellen.
3. Die Staging-Instanz ist erreichbar.
4. Die edu-sharing-API antwortet.
5. Anonymer Lesezugriff funktioniert.

---

### Suche gegen Staging testen

Als zweiten Test kann eine echte Suche ausgeführt werden.

Eine Datei `test_search.py` anlegen:

```python
from edusharing import Repository


REPOSITORY_URL = "https://repository.staging.openeduhub.net"


with Repository(REPOSITORY_URL, metadataset="mds_oeh") as repo:
    ergebnis = repo.search(
        "Photosynthese",
        subject="Biologie",
        limit=5,
    )

    print(f"Gefundene Ergebnisse: {ergebnis.total}")

    for treffer in ergebnis.hits:
        print()
        print("Titel:", treffer.title)
        print("URL:", treffer.url)
```

Ausführen:

```bash
python test_search.py
```

`mds_oeh` wird hier bewusst als Metadatensatz gewählt, weil der Filter `subject="Biologie"` dort verfügbar ist.

Wenn Treffer zurückkommen, ist der Client installiert, die Verbindung funktioniert und eine echte Suche gegen edu-sharing wurde erfolgreich ausgeführt.

---

### Zugangsdaten verwenden

Für öffentliche Lesezugriffe sind je nach Repositorium keine Zugangsdaten erforderlich.

Schreibende oder geschützte Operationen benötigen dagegen ein edu-sharing-Konto.

Zugangsdaten können direkt übergeben werden:

```python
from edusharing import Repository


with Repository(
    "https://repository.example.org",
    auth=("benutzer", "passwort"),
) as repo:
    print(repo.whoami())
```

Für Anwendungen und Entwicklungsumgebungen empfiehlt sich die Verwendung von Umgebungsvariablen:

```text
EDU_SHARING_URL
EDU_SHARING_USER
EDU_SHARING_PASSWORD
EDU_SHARING_METADATASET
```

Unter Windows PowerShell können sie beispielsweise für die aktuelle Sitzung gesetzt werden:

```powershell
$env:EDU_SHARING_URL="https://repository.example.org"
$env:EDU_SHARING_USER="benutzer"
$env:EDU_SHARING_PASSWORD="passwort"
$env:EDU_SHARING_METADATASET="mds_oeh"
```

Zugangsdaten sollten **nicht in die URL geschrieben werden**:

```text
https://benutzer:passwort@repository.example.org
```

Der Client lehnt diese Form bewusst ab, weil URLs in Logs und Fehlermeldungen auftauchen können.

---

### Bestehende Installation aktualisieren

#### Mit pip

Den aktuellen Stand von `main` installieren:

```bash
python -m pip install --upgrade "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

#### Mit uv

```bash
uv pip install --upgrade "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

---

### Eine bestimmte Version installieren

Wer nicht den aktuellen Stand von `main`, sondern eine bestimmte veröffentlichte Version verwenden möchte, kann einen Git-Tag angeben.

Mit pip:

```bash
python -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@v0.2.0"
```

Mit uv:

```bash
uv pip install "git+https://github.com/openeduhub/edu-sharing-python-client@v0.2.0"
```

`v0.2.0` ist eine ältere Veröffentlichung und enthält nicht die neueren Metadatenprofile und zusammengesetzten Flows aus dem aktuellen `main`.

> **Nicht `@v0.1.0`.** Dieser Tag stammt aus der Zeit vor mehreren Prüfrunden. `v0.2.0` ist der erste Tag, der deren Korrekturen enthält.

---

### Entwicklungsinstallation aus einer lokalen Arbeitskopie

Wer am Client selbst entwickeln, die Tests ausführen oder die Beispiele aus dem Repository verwenden möchte, sollte das Repository lokal klonen.

```bash
git clone https://github.com/openeduhub/edu-sharing-python-client.git
cd edu-sharing-python-client
```

#### Mit pip

Unter Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Unter Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

`-e` steht für eine **editable installation**. Änderungen am lokalen Quellcode stehen dadurch unmittelbar in der Python-Umgebung zur Verfügung, ohne das Paket nach jeder Änderung neu installieren zu müssen.

#### Mit uv

Für die vollständige Entwicklungsumgebung einschließlich der für Tests und Beispiele benötigten Abhängigkeiten:

```bash
uv sync
```

Alternativ kann auch eine editable installation explizit ausgeführt werden:

```bash
uv pip install -e .
```

---

### Tests ausführen

Die Offline-Tests laufen deterministisch und benötigen keine Verbindung zu einer edu-sharing-Instanz:

```bash
uv run pytest
```

Live-Tests können gegen die Staging-Instanz ausgeführt werden.

Unter Linux/macOS:

```bash
EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
```

Unter Windows PowerShell:

```powershell
$env:EDU_SHARING_URL="https://repository.staging.openeduhub.net"
uv run pytest -m live
```

Die schreibenden Tests (`-m write`) benötigen gültige Zugangsdaten. Sie arbeiten ausschließlich in einem eigenen Wegwerf-Ordner, den sie selbst anlegen und wieder entfernen.

---

### Lokale Arbeitskopie aktualisieren

Wer das Repository geklont hat, aktualisiert zunächst die Git-Arbeitskopie:

```bash
git pull
```

Bei einer pip-Entwicklungsinstallation bleibt `-e` mit der lokalen Arbeitskopie verbunden. Falls sich Paket-Metadaten oder Abhängigkeiten geändert haben, kann erneut ausgeführt werden:

```bash
python -m pip install -e .
```

Mit uv:

```bash
git pull
uv sync
```

---

### Fehlerbehebung

#### `python` wird unter Windows nicht gefunden

Zuerst den Python Launcher ausprobieren:

```powershell
py --version
```

Falls das funktioniert, können die entsprechenden Befehle mit `py` ausgeführt werden:

```powershell
py -m venv .venv
py -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

Falls auch `py` nicht gefunden wird, muss Python 3.11 oder neuer installiert werden.

---

#### `git` wird nicht gefunden

Prüfen:

```powershell
git --version
```

Falls Git nicht installiert ist, Git installieren und anschließend PowerShell bzw. das Terminal neu öffnen:

https://git-scm.com/downloads

---

#### PowerShell kann `Activate.ps1` nicht ausführen

Für die aktuelle PowerShell-Sitzung:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Danach erneut:

```powershell
.\.venv\Scripts\Activate.ps1
```

Die Änderung gilt nur für den aktuellen PowerShell-Prozess.

---

#### `ModuleNotFoundError: No module named 'edusharing'`

Prüfen, ob die virtuelle Umgebung aktiv ist. Unter Windows sollte der Prompt beispielsweise mit `(.venv)` beginnen:

```text
(.venv) PS C:\dev\edu-sharing-test>
```

Anschließend den Import direkt testen:

```bash
python -c "from edusharing import Repository; print('OK')"
```

Falls das nicht funktioniert, die Installation erneut ausführen.

Mit pip:

```bash
python -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

Mit uv:

```bash
uv pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

---

#### Installation funktioniert, aber Staging ist nicht erreichbar

Zuerst nur den Import testen:

```bash
python -c "from edusharing import Repository; print('OK')"
```

Funktioniert dieser Befehl, ist die Python-Bibliothek grundsätzlich korrekt installiert.

Scheitert dagegen:

```bash
python test_connection.py
```

liegt das Problem wahrscheinlich bei der Netzwerkverbindung oder der Erreichbarkeit des Repositoriums und nicht bei der Python-Installation.

Unternehmens-Proxys, VPNs, Firewalls oder TLS-Inspection können beispielsweise verhindern, dass Python die Staging-Instanz erreicht.