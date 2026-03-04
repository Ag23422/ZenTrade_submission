from fastapi import FastAPI, UploadFile, File,Form
import os
import json
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from master.input_handler import get_transcript
from master.hybrid_extrac import hybrid_extract
from master.prompt_gen import generate_prompt
from master.patch_engine import apply_patch
from master.diifrence import generate_diff
from master.state import account_seen, register_account
import sqlite3
import json
import re

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "temp_uploads"
OUTPUT_DIR = "outputs/accounts"

os.makedirs(UPLOAD_DIR, exist_ok=True)


DB_PATH = "clara.db"




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

            # company usually second group
            if len(match.groups()) > 1:
                return match.group(2).strip().replace(" ", "_")

            return match.group(1).strip().replace(" ", "_")

    return None
    
    
def resolve_account_id(filename, transcript, account_id=None):

    # priority 1: provided account id
    if account_id:
        return account_id

    # priority 2: detect company name
    company = extract_company_name(transcript)

    if company:
        return company

    # fallback: filename
    return filename.split(".")[0]
    
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

def save_upload(file: UploadFile):

    path = os.path.join(UPLOAD_DIR, file.filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path

@app.get("/", response_class=HTMLResponse)
def homepage():

    with open("static/index.html") as f:
        return f.read()

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

    memo = hybrid_extract(transcript)

    save_v1(account_id, memo)

    return {
        "account_id": account_id,
        "version": "v1",
        "memo": memo
    }

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

    patch = hybrid_extract(transcript)

    current = get_latest(account_id)

    if not current:
        return {"error": "demo call not processed"}

    current.update(patch)

    save_v2(account_id, current)

    return {
        "account_id": account_id,
        "version": "v2",
        "memo": current
    }

@app.get("/account/{account_id}")
def get_account(account_id: str):

    base = f"{OUTPUT_DIR}/{account_id}"

    if not os.path.exists(base):
        return {"error": "Account not found"}

    data = {}

    for root, dirs, files in os.walk(base):
        for file in files:

            if file.endswith(".json"):

                path = os.path.join(root, file)

                with open(path) as f:
                    data[file] = json.load(f)

    return data
    
@app.get("/db/accounts")
def get_accounts():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("SELECT * FROM accounts").fetchall()

    conn.close()

    return rows
