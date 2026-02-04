import requests
from flask import current_app


def create_incident(payload):
    url = f"{current_app.config['SERVICENOW_INSTANCE']}/api/now/table/incident"

    response = requests.post(
        url,
        auth=(
            current_app.config["SERVICENOW_USER"],
            current_app.config["SERVICENOW_PASSWORD"],
        ),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def check_existing_incident(short_description):
    """
    Check if an active incident with the same short description already exists
    Returns the incident details if found, None otherwise
    """
    url = f"{current_app.config['SERVICENOW_INSTANCE']}/api/now/table/incident"
    
    query = f"active=true^short_description={short_description}"
    
    response = requests.get(
        url,
        auth=(
            current_app.config["SERVICENOW_USER"],
            current_app.config["SERVICENOW_PASSWORD"],
        ),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        params={
            "sysparm_query": query,
            "sysparm_limit": 1,
            "sysparm_fields": "number,sys_id,short_description"
        },
        timeout=30
    )
    
    response.raise_for_status()
    result = response.json()
    
    if result.get("result") and len(result["result"]) > 0:
        return result["result"][0]
    return None
 