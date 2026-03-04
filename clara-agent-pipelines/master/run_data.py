import requests
import os

DATASET_DIR = "dataset"
API = "http://127.0.0.1:8000"

stats = {
    "demo_processed": 0,
    "onboarding_processed": 0,
    "errors": 0
}


def send_demo(path):

    try:

        with open(path, "rb") as f:

            files = {"file": f}

            r = requests.post(f"{API}/demo-call", files=files)

        if r.status_code == 200:

            stats["demo_processed"] += 1

            data = r.json()

            print(f"DEMO OK → {data['account_id']}")

        else:

            stats["errors"] += 1

    except Exception as e:

        stats["errors"] += 1
        print("DEMO ERROR:", e)


def send_onboarding(path):

    try:

        with open(path, "rb") as f:

            files = {"file": f}

            r = requests.post(f"{API}/onboarding-call", files=files)

        if r.status_code == 200:

            stats["onboarding_processed"] += 1

            data = r.json()

            print(f"ONBOARDING OK → {data['account_id']}")

        else:

            stats["errors"] += 1

    except Exception as e:

        stats["errors"] += 1
        print("ONBOARD ERROR:", e)


def main():

    files = sorted(os.listdir(DATASET_DIR))

    demo = [f for f in files if "demo" in f]
    onboard = [f for f in files if "onboarding" in f]

    print("\nRunning Demo Calls\n")

    for f in demo:

        send_demo(os.path.join(DATASET_DIR, f))

    print("\nRunning Onboarding Calls\n")

    for f in onboard:

        send_onboarding(os.path.join(DATASET_DIR, f))

    print("\n===== SUMMARY =====")

    print("Demo processed:", stats["demo_processed"])
    print("Onboarding processed:", stats["onboarding_processed"])
    print("Errors:", stats["errors"])


if __name__ == "__main__":
    main()
