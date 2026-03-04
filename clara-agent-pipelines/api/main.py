from fastapi import FastAPI, UploadFile, File, Form
import os
import json
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from master.input_handler import get_transcript
from master.hybrid_extrac import hybrid_extract
from master.prompt_gen import generate_agent_spec
from master.patch_engine import apply_patch
from master.diifrence import generate_diff
from master.state import account_seen, register_account

import sqlite3
import re


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "temp_uploads"
OUTPUT_DIR = "outputs/accounts"

os.makedirs(UPLOAD_DIR, exist_ok=True)

DB_PATH = "clara.db"


# -----------------------------
# COMPANY NAME EXTRACTION
# -----------------------------
def extract_company_name(text):

    text = text.lower()

    patterns = [
        r"this is (\w+)\sfrom\s([a-z\s]+)",
        r"hello.*from\s([a-z\s]+)",
        r"company\sname\sis\s([a-z\s]+)"
    ]

    for p in patterns:

        match = re.search(p, text)

        if match:

            if len(match.groups()) > 1:
                return match.group(2).strip().replace(" ", "_")

            return match.group(1).strip().replace(" ", "_")

    return None


# -----------------------------
# ACCOUNT ID RESOLUTION
# -----------------------------
def resolve_account_id(filename, transcript, account_id=None):

    if account_id:
        return account_id

    company = extract_company_name(transcript)

    if company:
        return company

    return filename.split(".")[0]


# -----------------------------
# DATABASE HELPERS
# -----------------------------
def get_latest(account_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT memo_json
        FROM agent_versions
        WHERE account_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (account_id,)
    ).fetchone()

    conn.close()

    if row:
        return json.loads(row[0])

    return None


def init_db():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT,
        version TEXT,
        memo_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()


# -----------------------------
# SAVE VERSIONS
# -----------------------------
def save_v1(account_id, memo):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO accounts(id) VALUES(?)",
        (account_id,)
    )

    cur.execute(
        """
        INSERT INTO agent_versions(account_id,version,memo_json)
        VALUES(?,?,?)
        """,
        (
            account_id,
            "v1",
            json.dumps(memo)
        )
    )

    conn.commit()
    conn.close()


def save_v2(account_id, memo):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO agent_versions(account_id,version,memo_json)
        VALUES(?,?,?)
        """,
        (
            account_id,
            "v2",
            json.dumps(memo)
        )
    )

    conn.commit()
    conn.close()


# -----------------------------
# FILE UPLOAD
# -----------------------------
def save_upload(file: UploadFile):

    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path


# -----------------------------
# UI
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def homepage():

    with open("static/index.html") as f:
        return f.read()


# -----------------------------
# DEMO CALL PIPELINE
# -----------------------------
@app.post("/demo-call")
async def demo_call(
    file: UploadFile = File(...),
    account_id: str = Form(None)
):

    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    transcript = get_transcript(path)

    account_id = resolve_account_id(
        file.filename,
        transcript,
        account_id
    )

    memo = hybrid_extract(transcript, account_id)

    agent_spec = generate_agent_spec(memo, "v1")

    save_v1(account_id, memo)

    return {
        "account_id": account_id,
        "version": "v1",
        "memo": memo,
        "agent_spec": agent_spec
    }


# -----------------------------
# ONBOARDING PIPELINE
# -----------------------------
@app.post("/onboarding-call")
async def onboarding_call(
    file: UploadFile = File(...),
    account_id: str = Form(None)
):

    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    transcript = get_transcript(path)

    account_id = resolve_account_id(
        file.filename,
        transcript,
        account_id
    )

    patch = hybrid_extract(transcript, account_id)

    current = get_latest(account_id)

    if not current:
        return {"error": "demo call not processed"}

    updated = apply_patch(current, patch)

    diff = generate_diff(current, updated)

    agent_spec = generate_agent_spec(updated, "v2")

    save_v2(account_id, updated)

    return {
        "account_id": account_id,
        "version": "v2",
        "memo": updated,
        "agent_spec": agent_spec,
        "changes": diff
    }


# -----------------------------
# ACCOUNT VIEWER
# -----------------------------
@app.get("/account/{account_id}")
def get_account(account_id: str):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT version, memo_json
        FROM agent_versions
        WHERE account_id=?
        ORDER BY id
        """,
        (account_id,)
    ).fetchall()

    conn.close()

    data = {}

    for version, memo in rows:
        data[version] = json.loads(memo)

    if "v1" in data and "v2" in data:
        diff = generate_diff(data["v1"], data["v2"])
    else:
        diff = None

    return {
        "account_id": account_id,
        "versions": data,
        "diff": diff
    }


# -----------------------------
# LIST ACCOUNTS
# -----------------------------
@app.get("/db/accounts")
def get_accounts():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("SELECT * FROM accounts").fetchall()

    conn.close()

    return rows
