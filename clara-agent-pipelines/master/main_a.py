import os
import json

from input_handler import get_transcript
from hybrid_extrac import hybrid_extract
from prompt_gen import generate_prompt
from state import account_seen, register_account

INPUT_DIR = "dataset/demo_calls"
OUTPUT_DIR = "outputs/accounts"


for file in os.listdir(INPUT_DIR):

    account_id = file.split(".")[0]

    if account_seen(account_id):
        continue

    file_path = os.path.join(INPUT_DIR, file)

    transcript = get_transcript(file_path)

    if not transcript.strip():
        continue

    memo = hybrid_extract(transcript)

    prompt = generate_prompt(memo)

    account_dir = f"{OUTPUT_DIR}/{account_id}/v1"
    os.makedirs(account_dir, exist_ok=True)

    with open(f"{account_dir}/memo.json", "w") as f:
        json.dump(memo, f, indent=2)

    with open(f"{account_dir}/agent_spec.json", "w") as f:
        json.dump({"version": "v1", "prompt": prompt}, f, indent=2)

    register_account(account_id)

    print("Processed demo:", account_id)
