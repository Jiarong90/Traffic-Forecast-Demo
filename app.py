from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

LTA_API_KEY = os.getenv("LTA_API_KEY")
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
SUPABASE_URL = "https://vwywaannhemxefrrqrtv.supabase.co"
SUPABASE_API_KEY = "sb_publishable_FfuRkw4At-Nlko5mVXoGaQ_ib_jrEFr"

app = FastAPI()

def require_user(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not Logged In")
    r = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "Authorization": authorization,
            "apikey": SUPABASE_API_KEY
        },
        timeout=5,
    )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return r.json()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/success")
def success():
    return FileResponse("static/index.html")

@app.get("/api/incidents")
def get_incidents(authorization: str | None = Header(default=None)):

    if not LTA_API_KEY:
        return load_placeholder_incidents(num_incidents, reason="missing_lta_api_key")


    user = require_user(authorization)
    url_incidents = "https://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"
    headers = {
        "AccountKey": LTA_API_KEY,
        "accept": "application/json"
    }
    num_incidents = 30

    
    try:
        response = requests.get(url_incidents, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        incidents = data.get("value", [])
        return {"incidents": incidents[:num_incidents], "user_id": user["id"]}
    except Exception:
        return load_placeholder_incidents(num_incidents, reason="lta_request_failed")

def load_placeholder_incidents(num_incidents: int, reason: str):
    try:
        with open("static/placeholder_incidents.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            incidents = data
        else:
            incidents = data.get("value", [])
        return {
            "source": "placeholder",
            "incidents": incidents[:num_incidents],
            "reason": reason
        }
    except Exception as e:
        return {
            "incidents": [],
            "reason": "Failed to load.."
        }