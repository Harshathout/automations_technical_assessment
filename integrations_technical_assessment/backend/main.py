from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import traceback

# Airtable
from integrations.airtable import (
    authorize_airtable,
    oauth2callback_airtable,
    get_airtable_credentials,
    get_items_airtable,
)

# Notion
from integrations.notion import (
    authorize_notion,
    oauth2callback_notion,
    get_notion_credentials,
    get_items_notion,
)

# HubSpot router ONLY
from integrations.hubspot import router as hubspot_router

app = FastAPI()

# ===============================
# CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Debug middleware
# ===============================
@app.middleware("http")
async def log_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception:
        print("\n🔥 FULL ERROR TRACEBACK 🔥")
        traceback.print_exc()
        raise

# ===============================
# Health
# ===============================
@app.get("/")
def read_root():
    return {"Ping": "Pong"}

# ===============================
# Airtable
# ===============================
@app.post("/integrations/airtable/authorize")
async def airtable_authorize(user_id: str = Form(...), org_id: str = Form(...)):
    return await authorize_airtable(user_id, org_id)

@app.get("/integrations/airtable/oauth2callback")
async def airtable_callback(request: Request):
    return await oauth2callback_airtable(request)

@app.post("/integrations/airtable/credentials")
async def airtable_credentials(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_airtable_credentials(user_id, org_id)

@app.post("/integrations/airtable/load")
async def airtable_load(credentials: str = Form(...)):
    return await get_items_airtable(credentials)

# ===============================
# Notion
# ===============================
@app.post("/integrations/notion/authorize")
async def notion_authorize(user_id: str = Form(...), org_id: str = Form(...)):
    return await authorize_notion(user_id, org_id)

@app.get("/integrations/notion/oauth2callback")
async def notion_callback(request: Request):
    return await oauth2callback_notion(request)

@app.post("/integrations/notion/credentials")
async def notion_credentials(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_notion_credentials(user_id, org_id)

@app.post("/integrations/notion/load")
async def notion_load(credentials: str = Form(...)):
    return await get_items_notion(credentials)

# ===============================
# HubSpot (ROUTER ONLY)
# ===============================
app.include_router(hubspot_router)
