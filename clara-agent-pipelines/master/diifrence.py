import json
from deepdiff import DeepDiff

def generate_diff(v1, v2):

    diff = DeepDiff(v1, v2, ignore_order=True)

    return diff
