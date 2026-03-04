import requests
import os

DATASET_DIR = "dataset"
API_URL = "http://127.0.0.1:8000"

def run_demo(file_path):

    with open(file_path, "rb") as f:

        files = {"file": f}

        r = requests.post(f"{API_URL}/demo-call", files=files)

        print("\n--- DEMO ---")
        print(file_path)
        print(r.json())


def run_onboarding(file_path):

    with open(file_path, "rb") as f:

        files = {"file": f}

        r = requests.post(f"{API_URL}/onboarding-call", files=files)

        print("\n--- ONBOARDING ---")
        print(file_path)
        print(r.json())


def main():

    files = sorted(os.listdir(DATASET_DIR))

    demo_files = [f for f in files if "demo" in f]
    onboarding_files = [f for f in files if "onboarding" in f]

    for f in demo_files:

        run_demo(os.path.join(DATASET_DIR, f))

    for f in onboarding_files:

        run_onboarding(os.path.join(DATASET_DIR, f))


if __name__ == "__main__":
    main()
