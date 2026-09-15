## Installing

The client requires **Python 3.11 or newer**.

The package is currently **not published on PyPI**. Install it directly from the Git repository.

For most users, using a **virtual Python environment (`venv`)** is recommended. This keeps the edu-sharing client and its dependencies isolated from other Python projects.

### Requirements

Before installing, make sure the following tools are available:

- Python 3.11 or newer
- Git
- pip (included with normal Python installations)

Check your Python version:

```bash
python --version
```

Expected output, for example:

```text
Python 3.12.10
```

Check Git:

```bash
git --version
```

Expected output, for example:

```text
git version 2.51.0.windows.1
```

If `python` or `git` is not found, install Python from [python.org](https://www.python.org/downloads/) and Git from [git-scm.com](https://git-scm.com/downloads) first.

---

### Windows installation

The following example uses **PowerShell**.

Create a directory for your project:

```powershell
mkdir C:\dev\edu-sharing-test
cd C:\dev\edu-sharing-test
```

Create a virtual Python environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the PowerShell prompt should start with `(.venv)`, for example:

```text
(.venv) PS C:\dev\edu-sharing-test>
```

If PowerShell refuses to execute `Activate.ps1` because script execution is disabled, you can enable scripts for the current PowerShell process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the current version of the edu-sharing Python client directly from GitHub:

```powershell
python -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

The required runtime dependencies, including `httpx` and `attrs`, are installed automatically.

---

### Linux and macOS installation

Create a project directory:

```bash
mkdir -p ~/edu-sharing-test
cd ~/edu-sharing-test
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the client:

```bash
python -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

---

### Installation with uv

If you already use [uv](https://docs.astral.sh/uv/), the client can also be installed with:

```bash
uv pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

To update an existing installation:

```bash
uv pip install --upgrade "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

With regular pip:

```bash
python -m pip install --upgrade "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

---

### Verify the installation

Start Python:

```bash
python
```

Then try importing the library:

```python
from edusharing import Repository

print("edu-sharing Python client successfully installed")
```

Exit Python with:

```python
exit()
```

If no import error occurs, the package is installed correctly.

---

## Test the connection against edu-sharing staging

The public staging repository can be used for a simple read-only connection test:

```text
https://repository.staging.openeduhub.net
```

No username or password is required for this test.

Create a file named:

```text
test_connection.py
```

with the following content:

```python
from edusharing import Repository


REPOSITORY_URL = "https://repository.staging.openeduhub.net"


with Repository(REPOSITORY_URL) as repo:
    about = repo.about()
    who = repo.whoami()

    print("Connection successful")
    print("Repository version:", about.repository_version)
    print("Plugins:", about.plugins)
    print("Current authority:", who.authority)
```

Run it:

```bash
python test_connection.py
```

A successful connection should produce output similar to:

```text
Connection successful
Repository version: 11.0
Plugins: [...]
Current authority: esguest
```

`esguest` means that the request is running anonymously.

This verifies several things at once:

1. Python can import the `edusharing` package.
2. The client can establish an HTTPS connection.
3. The staging repository is reachable.
4. The edu-sharing REST API responds correctly.
5. Anonymous read access works.

---

## Test a search against staging

You can also perform a real search.

Create a file named:

```text
test_search.py
```

with:

```python
from edusharing import Repository


REPOSITORY_URL = "https://repository.staging.openeduhub.net"


with Repository(REPOSITORY_URL, metadataset="mds_oeh") as repo:
    result = repo.search(
        "Photosynthese",
        subject="Biologie",
        limit=5,
    )

    print(f"Found {result.total} results")

    for hit in result.hits:
        print()
        print("Title:", hit.title)
        print("URL:", hit.url)
```

Run it:

```bash
python test_search.py
```

The `mds_oeh` metadata set is explicitly selected because the `subject` filter is available there.

If this test returns search results, the client is ready to use.

---

## Using credentials

Anonymous access is sufficient for public read operations.

Operations such as creating or modifying material require an authenticated edu-sharing account.

Credentials can be passed directly:

```python
from edusharing import Repository


with Repository(
    "https://repository.example.org",
    auth=("username", "password"),
) as repo:
    print(repo.whoami())
```

For applications and development environments, environment variables are recommended instead:

```text
EDU_SHARING_URL
EDU_SHARING_USER
EDU_SHARING_PASSWORD
EDU_SHARING_METADATASET
```

Do **not** put credentials into the URL:

```text
https://username:password@repository.example.org
```

The client deliberately refuses this form because URLs can appear in logs and error messages.

---

## Installing a specific version

The project is currently pre-1.0.

To install the existing `v0.2.0` release instead of the current `main` branch:

```bash
python -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@v0.2.0"
```

Or with uv:

```bash
uv pip install "git+https://github.com/openeduhub/edu-sharing-python-client@v0.2.0"
```

Note that `v0.2.0` does not contain the newer functionality currently available on `main`.

---

## Development installation

If you want to modify the client itself, run its tests, or execute the examples from the repository, clone the repository instead of installing it directly from Git.

```bash
git clone https://github.com/openeduhub/edu-sharing-python-client.git
cd edu-sharing-python-client
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the checkout in editable mode:

```bash
python -m pip install -e .
```

Changes to the local source code are then immediately available without reinstalling the package.

If you use uv and want the complete development environment, including dependencies needed by the tests and examples:

```bash
uv sync
```

Run the offline test suite with:

```bash
uv run pytest
```

Live read-only tests can be run against staging:

```bash
EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
```

On Windows PowerShell, set the environment variable first:

```powershell
$env:EDU_SHARING_URL="https://repository.staging.openeduhub.net"
uv run pytest -m live
```

Write tests require valid credentials and should only be run when you intentionally want to test write operations.

---

## Updating the client

If the client was installed directly from GitHub using pip:

```bash
python -m pip install --upgrade "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

If you cloned the repository for development:

```bash
git pull
python -m pip install -e .
```

or, when using uv:

```bash
git pull
uv sync
```

---

## Troubleshooting

### `python` is not recognized

Try:

```powershell
py --version
```

If the Python Launcher is installed, you can use:

```powershell
py -m venv .venv
py -m pip install "git+https://github.com/openeduhub/edu-sharing-python-client@main"
```

Otherwise install Python 3.11 or newer and make sure Python is available in `PATH`.

### `git` is not recognized

Install Git and restart PowerShell or your terminal afterwards:

https://git-scm.com/downloads

Then verify:

```bash
git --version
```

### PowerShell cannot run `Activate.ps1`

For the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

This changes the execution policy only for the current PowerShell process.

### `ModuleNotFoundError: No module named 'edusharing'`

Make sure the virtual environment is active:

```text
(.venv)
```

Then check the installation:

```bash
python -m pip show edu-sharing
```

You can also test the import directly:

```bash
python -c "from edusharing import Repository; print('OK')"
```

### Connection to staging fails

First check whether the staging repository itself is reachable:

```text
https://repository.staging.openeduhub.net
```

Corporate proxies, VPNs, firewalls or TLS inspection can prevent Python from reaching the repository even when the installation itself is correct.

The import test and connection test are deliberately separate: if

```bash
python -c "from edusharing import Repository; print('OK')"
```

works but `test_connection.py` fails, the package is installed and the problem is related to the connection or repository rather than the Python installation.