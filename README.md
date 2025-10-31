# MuseHub — Flask + PostgreSQL Quickstart

A tiny Flask web app (for Columbia COMS W4111) that connects to a PostgreSQL DB and renders simple pages.

## Stack
- Python 3.10+
- Flask
- SQLAlchemy
- PostgreSQL driver (`psycopg2-binary`)
- (Optional) `python-dotenv` for `.env` loading

---

## 0) Prerequisites
- **Python 3.10+** installed. If you use `pyenv`, set project version:
    ```bash
    pyenv local 3.10.14
    ```
- Clone & enter the project
    ```bash
    git clone https://github.com/MichaelCheng0707/MuseHub.git
    cd MuseHub
    ```
- Create & activate a virtual environment
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

- Install dependencies
    ```bash
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    ```

- Create .env file to store DB_USER, DB_PASS
    ```
    DB_USER=YOUR_UNI
    DB_PASS=YOUR_PASSWORD
    ```

- Run the server
    ```
    ./.venv/bin/python server.py
    ```