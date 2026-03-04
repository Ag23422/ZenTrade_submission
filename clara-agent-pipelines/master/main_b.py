import os
import json

from input_handler import get_transcript
from hybrid_extrac import hybrid_extract
from patch_engine import apply_patch
from diifrence import generate_diff

INPUT_DIR = "dataset/onboarding_calls"
OUTPUT_DIR = "outputs/accounts"


for file in os.listdir(INPUT_DIR):

    account_id = file.split(".")[0]

    v1_path = f"{OUTPUT_DIR}/{account_id}/v1/memo.json"

    if not os.path.exists(v1_path):
        continue

    file_path = os.path.join(INPUT_DIR, file)

    transcript = get_transcript(file_path)

    if not transcript.strip():
        continue

    patch = hybrid_extract(transcript)

    with open(v1_path) as f:
        v1 = json.load(f)

    v2 = apply_patch(v1, patch)

    v2_dir = f"{OUTPUT_DIR}/{account_id}/v2"
    os.makedirs(v2_dir, exist_ok=True)

    v2_path = f"{v2_dir}/memo.json"

    with open(v2_path, "w") as f:
        json.dump(v2, f, indent=2)

    diff = generate_diff(v1_path, v2_path)

    with open(f"{OUTPUT_DIR}/{account_id}/changes.json", "w") as f:
        json.dump(diff, f, indent=2)

    print("Processed onboarding:", account_id)
