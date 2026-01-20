from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
from dotenv import load_dotenv
import os

load_dotenv()

LTA_API_KEY = os.getenv("LTA_API_KEY")
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
if not LTA_API_KEY or not DATA_GOV_API_KEY:
    raise Exception("API Key not found")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/api/incidents")
def get_incidents():
    url_incidents = "https://datamall2.mytransport.sg/ltaodataservice/TrafficIncidents"
    headers = {
        "AccountKey": LTA_API_KEY,
        "accept": "application/json"
    }
    num_incidents = 20

    data = requests.get(url_incidents, headers=headers).json()
    incidents = data.get("value", [])
    return {"incidents": incidents[:num_incidents]}