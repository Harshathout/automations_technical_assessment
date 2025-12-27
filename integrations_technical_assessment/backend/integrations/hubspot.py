import os
import json
import requests
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

from integrations.integration_item import IntegrationItem
from redis_client import redis_client

load_dotenv()

HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
HUBSPOT_REDIRECT_URI = "http://localhost:8000/integrations/hubspot/oauth2callback"

AUTH_URL = "https://app.hubspot.com/oauth/authorize"
TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"
API_BASE_URL = "https://api.hubapi.com"

router = APIRouter(prefix="/integrations/hubspot")

# ===============================
# PART 1 — AUTHORIZE
# ===============================

@router.get("/authorize")
async def authorize(user_id: str, org_id: str):
    state = f"{user_id}:{org_id}"

    scope = (
        "crm.objects.contacts.read "
        "crm.objects.contacts.write "
        "crm.objects.companies.read "
        "crm.objects.companies.write"
    )

    params = {
        "client_id": HUBSPOT_CLIENT_ID,
        "redirect_uri": HUBSPOT_REDIRECT_URI,
        "scope": scope,
        "response_type": "code",
        "state": state,
    }

    url = requests.Request("GET", AUTH_URL, params=params).prepare().url
    return RedirectResponse(url)

# ===============================
# PART 1 — CALLBACK
# ===============================

@router.get("/oauth2callback")
async def oauth2callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    user_id, org_id = state.split(":")

    data = {
        "grant_type": "authorization_code",
        "client_id": HUBSPOT_CLIENT_ID,
        "client_secret": HUBSPOT_CLIENT_SECRET,
        "redirect_uri": HUBSPOT_REDIRECT_URI,
        "code": code,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    response.raise_for_status()

    credentials = response.json()

    key = f"hubspot_credentials:{user_id}:{org_id}"
    await redis_client.set(key, json.dumps(credentials))

    return {"message": "HubSpot authorization successful"}

# ===============================
# GET STORED CREDENTIALS
# ===============================

@router.post("/credentials")
async def get_credentials(
    user_id: str = Form(...),
    org_id: str = Form(...)
):
    key = f"hubspot_credentials:{user_id}:{org_id}"
    creds = await redis_client.get(key)

    if not creds:
        raise HTTPException(status_code=400, detail="No credentials found")

    return json.loads(creds)

# ===============================
# PART 2 — FETCH ITEMS
# ===============================

@router.post("/get_hubspot_items")
async def get_hubspot_items(credentials: str = Form(...)):
    import json
    import requests

    print("📥 RAW credentials:", credentials)

    try:
        creds = json.loads(credentials)
    except Exception as e:
        print("❌ JSON ERROR:", e)
        return {"error": "Invalid credentials JSON"}

    access_token = creds.get("access_token")

    if not access_token:
        return {"error": "Missing access_token"}

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    url = "https://api.hubapi.com/crm/v3/objects/contacts"

    response = requests.get(url, headers=headers)

    print("🔁 HubSpot status:", response.status_code)
    print("🔁 HubSpot response:", response.text)

    if response.status_code != 200:
        return {
            "error": "HubSpot API failed",
            "status": response.status_code,
            "details": response.text
        }

    data = response.json()

    items = []
    for c in data.get("results", []):
        props = c.get("properties", {})
        items.append({
            "id": c.get("id"),
            "name": props.get("firstname", ""),
            "email": props.get("email", "")
        })

    print("\n✅ HubSpot Integration Items:")
    for item in items:
        print(item)

    return items
