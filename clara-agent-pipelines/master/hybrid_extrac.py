
import re

EMERGENCY_KEYWORDS = [
    "sprinkler leak",
    "fire alarm",
    "alarm triggered",
    "water flow alarm"
]

NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12"
}

def normalize_numbers(text):

    words = text.split()

    converted = []

    for w in words:
        if w in NUMBER_WORDS:
            converted.append(NUMBER_WORDS[w])
        else:
            converted.append(w)

    return " ".join(converted)
    
def extract_business_hours(text):

    text = text.lower()

    # convert words like "eight" -> "8"
    text = normalize_numbers(text)

    # match numeric time patterns
    time_pattern = r"\b\d{1,2}(:\d{2})?\s?(am|pm)?\b"

    matches = re.finditer(time_pattern, text)

    detected_times = [m.group() for m in matches]

    if len(detected_times) >= 2:
        return {
            "start": detected_times[0],
            "end": detected_times[1]
        }

    return None

def rule_extract(text):

    data = {}

    hours = extract_business_hours(text)

    if hours:
        data["business_hours"] = hours

    services = []

    t = text.lower()

    if "sprinkler" in t:
        services.append("sprinkler")

    if "alarm" in t:
        services.append("alarm")

    if services:
        data["services_supported"] = services

    emergencies = []

    if "sprinkler leak" in t:
        emergencies.append("sprinkler leak")

    if "fire alarm" in t:
        emergencies.append("fire alarm")

    if emergencies:
        data["emergency_definition"] = emergencies

    return data


def hybrid_extract(text):

    result = rule_extract(text)

    result.setdefault("questions_or_unknowns", [])

    if "business_hours" not in result:
        result["questions_or_unknowns"].append(
            "business hours not specified"
        )

    return result
