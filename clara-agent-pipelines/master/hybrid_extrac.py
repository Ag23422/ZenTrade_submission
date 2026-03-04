import re

EMERGENCY_KEYWORDS = [
    "sprinkler leak",
    "fire alarm",
    "alarm triggered",
    "water flow alarm"
]

NUMBER_WORDS = {
    "one":"1","two":"2","three":"3","four":"4",
    "five":"5","six":"6","seven":"7","eight":"8",
    "nine":"9","ten":"10","eleven":"11","twelve":"12"
}


# -----------------------------
# TEXT NORMALIZATION
# -----------------------------

def normalize_numbers(text):

    words = text.split()
    converted = []

    for w in words:
        converted.append(NUMBER_WORDS.get(w, w))

    return " ".join(converted)


# -----------------------------
# COMPANY NAME
# -----------------------------

def extract_company_name(text):

    patterns = [
        r"this is .* from ([a-zA-Z\s]+)",
        r"hello .* from ([a-zA-Z\s]+)"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    return None


# -----------------------------
# ADDRESS
# -----------------------------

def extract_address(text):

    m = re.search(
        r"\d{2,5}\s+[A-Za-z\s]+(drive|dr|road|rd|street|st|avenue|ave)",
        text,
        re.IGNORECASE
    )

    if m:
        return m.group(0)

    return None


# -----------------------------
# BUSINESS HOURS
# -----------------------------

def extract_business_hours(text):

    text = text.lower()
    text = normalize_numbers(text)

    time_pattern = r"\b\d{1,2}(:\d{2})?\s?(am|pm)\b"

    matches = re.findall(time_pattern, text)
    numbers = re.findall(r"\d{1,2}\s?(?:am|pm)", text)

    if len(numbers) >= 2:
        return {
            "days": "Mon-Fri",
            "start": numbers[0],
            "end": numbers[1],
            "timezone": None
        }

    return None


# -----------------------------
# SERVICES
# -----------------------------

def extract_services(text):

    services = []
    t = text.lower()

    if "sprinkler" in t:
        services.append("sprinkler services")

    if "alarm" in t:
        services.append("fire alarm services")

    if "inspection" in t:
        services.append("inspection")

    return services


# -----------------------------
# EMERGENCY TRIGGERS
# -----------------------------

def extract_emergencies(text):

    t = text.lower()

    found = []

    for e in EMERGENCY_KEYWORDS:
        if e in t:
            found.append(e)

    return found


# -----------------------------
# INTEGRATION CONSTRAINTS
# -----------------------------

def extract_constraints(text):

    t = text.lower()

    constraints = []

    if "servicetrade" in t:
        constraints.append(
            "never create sprinkler jobs in ServiceTrade automatically"
        )

    return constraints


# -----------------------------
# ROUTING RULES (TEMPLATE)
# -----------------------------

def default_routing():

    return {

        "emergency_routing_rules":{
            "primary":"dispatch",
            "fallback":"voicemail"
        },

        "non_emergency_routing_rules":{
            "during_hours":"schedule service",
            "after_hours":"collect message"
        },

        "call_transfer_rules":{
            "attempts":2,
            "timeout_seconds":20,
            "fallback_message":
                "A dispatcher will return your call shortly."
        }

    }


# -----------------------------
# FLOW SUMMARIES
# -----------------------------

def flow_templates():

    return {

        "office_hours_flow_summary":
        "greet caller → ask purpose → collect name and number → "
        "determine emergency vs non-emergency → transfer or schedule → "
        "confirm next steps → ask if anything else → close",

        "after_hours_flow_summary":
        "greet caller → determine emergency → if emergency collect "
        "name number address immediately → attempt transfer → "
        "fallback if transfer fails → assure quick follow up → close"
    }


# -----------------------------
# MAIN RULE EXTRACTION
# -----------------------------

def rule_extract(text):

    data = {}

    data["company_name"] = extract_company_name(text)

    hours = extract_business_hours(text)
    if hours:
        data["business_hours"] = hours

    address = extract_address(text)
    if address:
        data["office_address"] = address

    services = extract_services(text)
    if services:
        data["services_supported"] = services

    emergencies = extract_emergencies(text)
    if emergencies:
        data["emergency_definition"] = emergencies

    constraints = extract_constraints(text)
    if constraints:
        data["integration_constraints"] = constraints

    return data


# -----------------------------
# FINAL MEMO BUILDER
# -----------------------------

def hybrid_extract(text, account_id="unknown"):

    result = rule_extract(text)

    memo = {
        "account_id": account_id,
        "company_name": result.get("company_name"),
        "business_hours": result.get("business_hours"),
        "office_address": result.get("office_address"),
        "services_supported": result.get("services_supported", []),
        "emergency_definition": result.get("emergency_definition", []),
        "integration_constraints": result.get("integration_constraints", []),
        "notes": "generated from transcript"
    }

    memo.update(default_routing())
    memo.update(flow_templates())

    memo["questions_or_unknowns"] = []

    if not memo["company_name"]:
        memo["questions_or_unknowns"].append("company name missing")

    if not memo["business_hours"]:
        memo["questions_or_unknowns"].append("business hours missing")

    if not memo["emergency_definition"]:
        memo["questions_or_unknowns"].append(
            "emergency triggers not clearly defined"
        )

    return memo
