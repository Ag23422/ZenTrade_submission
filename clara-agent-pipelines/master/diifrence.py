import json
from deepdiff import DeepDiff


def generate_diff(v1_path, v2_path):

    with open(v1_path) as f:
        v1 = json.load(f)

    with open(v2_path) as f:
        v2 = json.load(f)

    return DeepDiff(v1, v2)
