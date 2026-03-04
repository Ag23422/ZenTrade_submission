def generate_agent_spec(memo, version="v1"):

    company = memo.get("company_name") or "Service Company"

    hours = memo.get("business_hours") or {}

    address = memo.get("office_address")

    emergency_triggers = memo.get("emergency_definition", [])

    transfer_rules = memo.get("call_transfer_rules", {})

    spec = {

        "agent_name": f"{company} Dispatcher",

        "voice_style": "professional calm helpful",

        "version": version,

        "key_variables": {

            "timezone": hours.get("timezone"),

            "business_hours": hours,

            "office_address": address,

            "emergency_triggers": emergency_triggers

        },

        "call_transfer_protocol": transfer_rules,

        "fallback_protocol":
        "If transfer fails collect caller name phone number and address "
        "and assure a dispatcher will call back shortly.",

        "system_prompt": build_prompt(memo)

    }

    return spec


def build_prompt(memo):

    company = memo.get("company_name")

    services = ", ".join(memo.get("services_supported", []))

    emergency = ", ".join(memo.get("emergency_definition", []))

    hours = memo.get("business_hours")

    address = memo.get("office_address")

    constraints = ", ".join(memo.get("integration_constraints", []))

    transfer = memo.get("call_transfer_rules", {})

    attempts = transfer.get("attempts", 2)

    timeout = transfer.get("timeout_seconds", 20)

    return f"""
You are a call handling assistant for {company}.

COMPANY INFORMATION
Business hours: {hours}
Office address: {address}

Services supported:
{services}

Emergency triggers include:
{emergency}

CALL TRANSFER PROTOCOL
- attempt transfer {attempts} times
- wait {timeout} seconds for answer
- if transfer fails collect caller name phone number and address
- assure the caller dispatch will return the call shortly

OFFICE HOURS FLOW
1 greet caller politely
2 ask purpose of call
3 collect caller name and phone number
4 determine emergency vs non emergency
5 if emergency transfer to dispatch immediately
6 if non emergency schedule service or take message
7 confirm next steps
8 ask if anything else is needed
9 close call politely

AFTER HOURS FLOW
1 greet caller politely
2 determine if situation is an emergency

If emergency:
- collect caller name phone number and address immediately
- attempt transfer to dispatch

If transfer fails:
- reassure caller help will arrive soon
- confirm their phone number

If non emergency:
- collect request details
- inform caller the office will respond during business hours

CONSTRAINTS
{constraints}

Never mention internal tools or system functions to the caller.
Only collect information necessary for routing and dispatch.
"""
