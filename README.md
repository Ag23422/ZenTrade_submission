# Clara AI Agent Pipeline

Live Deployment:

UI Interface  
https://zentrade-submission.onrender.com

API Endpoints (Swagger Docs)  
https://zentrade-submission.onrender.com/docs

This project implements an automated pipeline that converts **demo and onboarding call recordings/transcripts** into structured operational configurations for AI voice agents.

The system extracts structured information from calls, generates **Account Memo JSON**, creates **Retell Agent Draft Specifications**, and maintains **versioned updates (v1 → v2)** when onboarding calls introduce changes.

---

# System Architecture
                    +-----------------------+
                    |  Demo / Onboarding    |
                    |  Call Recording or    |
                    |  Transcript Upload    |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |   Input Handler       |
                    | Detect file type and  |
                    | extract transcript    |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |  Hybrid Extraction    |
                    | Rule-based extraction |
                    | of operational data   |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |  Account Memo JSON    |
                    | Structured data model |
                    | for the customer      |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |  Agent Spec Generator |
                    | Builds Retell Agent   |
                    | configuration + prompt|
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Version Storage       |
                    | SQLite database       |
                    | v1 / v2 configurations|
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | Diff Engine           |
                    | Detect changes        |
                    | between v1 and v2     |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | API + Minimal UI      |
                    | View outputs and diff |
                    +-----------------------+

---

# Key Features

## Demo Call Processing (Pipeline A)

Processes the initial demo call and generates:

- Account Memo JSON
- Retell Agent Draft Specification
- Version `v1` configuration

---

## Onboarding Update Processing (Pipeline B)

Processes onboarding calls and:

- Extracts new operational details
- Applies patch to existing memo
- Generates updated agent spec
- Stores version `v2`
- Generates a change diff showing what changed

---

## Hybrid Extraction Engine

The extraction system identifies:

- Company name
- Business hours
- Services supported
- Emergency triggers
- Integration constraints
- Office address

If information is missing, the system flags it under `questions_or_unknowns` instead of hallucinating values.

---

## Retell Agent Draft Spec Generation

The pipeline generates a structured agent specification including:

- Agent name
- Voice style
- System prompt
- Key variables
- Call transfer protocol
- Transfer fallback protocol
- Version identifier

---

# Project Structure
repo/

api/
main.py # FastAPI server and endpoints

master/
hybrid_extrac.py # Hybrid extraction engine
prompt_gen.py # Agent spec and prompt generator
input_handler.py # Audio/transcript processing
patch_engine.py # Update logic for onboarding
diifrence.py # Diff generation
state.py # Account registry logic

scripts/
run_dataset.py # Batch dataset runner

static/
index.html # Minimal UI

outputs/
accounts/ # Generated account outputs

requirements.txt
README.md

---

# API Endpoints

## Demo Call


POST /demo-call


Processes an initial demo call.

Returns:


{
account_id,
version,
memo,
agent_spec
}


---

## Onboarding Call


POST /onboarding-call


Updates an existing account configuration.

Returns:


{
account_id,
version,
memo,
agent_spec,
changes
}


---

## Account Viewer


GET /account/{account_id}


Displays:

- v1 configuration
- v2 configuration
- diff showing changes

---

## Accounts List


GET /db/accounts


Returns all processed accounts.

---

# Running the Project Locally

Install dependencies:


pip install -r requirements.txt


Run the API:


uvicorn api.main:app --reload


Open the interface:


http://localhost:8000


or API docs:


http://localhost:8000/docs

---

# Running with Docker

Build container:


docker build -t clara-agent .


Run container:


docker run -p 8000:8000 clara-agent


---

# Batch Dataset Processing

Run the dataset pipeline:


python scripts/run_dataset.py


This automatically processes all demo and onboarding files.

---

# Output Structure

Generated outputs are stored in:


outputs/accounts/<account_id>/


Example:


outputs/accounts/safesprinkler/

v1/
memo.json
agent_spec.json

v2/
memo.json
agent_spec.json

changes.json


---

# Retell Setup

To configure an agent in Retell:

1. Copy generated `agent_spec.json`
2. Paste the `system_prompt` into the Retell agent configuration
3. Set key operational variables
4. Configure call transfer rules

---

# LLM Usage

This implementation uses rule-based extraction to ensure zero-cost operation without relying on paid LLM APIs.

---

# Known Limitations

- Rule-based extraction may miss unusual phrasing
- Address extraction uses regex patterns
- Audio transcription accuracy depends on recording quality

---

# Future Improvements

Potential production improvements:

- LLM-assisted extraction
- n8n orchestration pipeline
- improved entity recognition
- richer UI dashboard
- automated Retell API integration

---
Running with Docker (Linux / Mac / Windows)

Install Docker Desktop:

https://www.docker.com/products/docker-desktop/

Clone the repository:

git clone https://github.com/Ag23422/ZenTrade_submission.git
cd ZenTrade_submission

Build the Docker image:

docker build -t clara-agent .

Run the container:

docker run -p 8000:8000 clara-agent

Open in browser:

http://localhost:8000

API documentation:

http://localhost:8000/docs
Windows PowerShell Example
git clone https://github.com/Ag23422/ZenTrade_submission.git
cd ZenTrade_submission

docker build -t clara-agent .

docker run -p 8000:8000 clara-agent

Then open:

http://localhost:8000

-------------

# Summary

This project demonstrates a modular and automated pipeline for converting customer calls into structured operational configurations for AI voice agents.

The system is designed to be:

- repeatable
- modular
- versioned
- easy to test
