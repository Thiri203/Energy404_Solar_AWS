"""
api.py — FastAPI backend for Energy404
---------------------------------------
Exposes REST endpoints for solar potential predictions.
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# === Ensure we can import from pipeline/ ===
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "pipeline"))

from predict import predict_energy  # ✅ same as app.py

app = FastAPI(
    title="Energy404 Solar Potential API",
    description="Predict annual rooftop solar energy potential (kWh/m²) for a given city, building type, and tilt.",
    version="1.0.0",
)

# ===== Input Schema =====
class PredictionRequest(BaseModel):
    city: str
    building_type: str
    tilt: float

# ===== Root Endpoint =====
@app.get("/")
def root():
    return {"message": "☀️ Energy404 API is running! Use POST /predict to get predictions."}

# ===== Allow City, Builting Type and Tilt Range =====
@app.get("/metadata")
def get_metadata():
    return {
        "cities": ['Colombo', 'Maldives', 'Karachi', 'Beirut', 'Antigua', 'Izmir',
       'Honduras', 'Panama', 'Nairobi', 'Lagos', 'LagosState',
       'Samarkand', 'Accra', 'Mexico City', 'SouthAfrica', 'DarEsSalaam',
       'Almaty', 'Manila', 'GreatDhakaRegion', 'Grenada'],
        "building_types": ['commercial', 'hotels', 'industrial', 'multifamily residential',
       'peri-urban settlement', 'public health facilities',
       'public sector', 'schools', 'single family residential',
       'small commercial'],
        "tilt_range": [0, 60]
    }

# ===== Prediction Endpoint =====
@app.post("/predict")
def get_prediction(req: PredictionRequest):
    try:
        pred_value = predict_energy(
            city=req.city,
            building_type=req.building_type,
            tilt=req.tilt
        )
        return {
            "city": req.city,
            "building_type": req.building_type,
            "tilt": req.tilt,
            "predicted_kWh_per_m2": pred_value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
