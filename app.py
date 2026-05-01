from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os

from src.api_logic import (
    run_ideal_simulation,
    run_noisy_simulation,
    run_hardware_execution,
    run_fidelity_analysis
)

app = FastAPI(title="Quantum Teleportation API")

os.makedirs("outputs", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/static", StaticFiles(directory="static"), name="static")

class StateRequest(BaseModel):
    state: str

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/api/ideal")
def ideal_sim(req: StateRequest):
    try:
        return run_ideal_simulation(req.state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/noisy")
def noisy_sim(req: StateRequest):
    try:
        return run_noisy_simulation(req.state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hardware")
def hardware_exec(req: StateRequest):
    try:
        return run_hardware_execution(req.state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fidelity")
def fidelity_analysis():
    try:
        return run_fidelity_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting FastAPI server on http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
