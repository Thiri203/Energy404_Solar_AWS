"""
predict.py — Energy404 Deployment Inference Pipeline (Lazy-loading version)
---------------------------------------------------------------------------
Loads pre-trained ensemble models (LGBM + XGB + RF + ET + Ridge meta)
on demand and predicts annual rooftop solar energy potential (kWh/m²).
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from functools import lru_cache

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models_local_backup"
DATA_DIR = BASE_DIR / "data"

# === Load config and weather once (small files) ===
print("🔹 Loading lightweight configuration...")
config = joblib.load(MODELS_DIR / "feature_config.pkl")
NUM = config["NUM"]
CAT = config["CAT"]
building_categories = config["BuildingType_categories"]

weather_path = DATA_DIR / "city_weather.csv"
weather_df = pd.read_csv(weather_path)

# === Lazy loaders for heavy model files ===
@lru_cache()
def load_model(name: str):
    """Loads and caches a single model or list of models by name."""
    path = MODELS_DIR / f"{name}.pkl"
    print(f"⚙️  Loading {name} from disk...")
    return joblib.load(path)

# === Core prediction function ===
def predict_energy(city: str, building_type: str, tilt: float) -> float:
    """
    Predict rooftop solar potential (kWh/m²/year)
    for the given city, building type, and roof tilt.
    """

    # --- Validate inputs ---
    if city not in weather_df["City"].values:
        raise ValueError(f"❌ City '{city}' not found in city_weather.csv")
    if building_type not in building_categories:
        raise ValueError(f"❌ BuildingType '{building_type}' not recognized")

    # --- Lookup city weather ---
    row = weather_df.loc[weather_df["City"] == city].iloc[0]
    GHI, Temp, Clear, Precip = row["avg_GHI_kWhm2_day"], row["avg_temp_C"], row["clearness_index"], row["precip_mm_day"]

    # --- Compute tilt features ---
    tilt2 = tilt ** 2
    tilt_sin, tilt_cos = np.sin(np.radians(tilt)), np.cos(np.radians(tilt))

    # --- Create full feature dict ---
    feats = {
        "tilt": tilt,
        "tilt2": tilt2,
        "tilt_sin": tilt_sin,
        "tilt_cos": tilt_cos,
        "GHI_kWh_per_m2_day": GHI,
        "AvgTemp_C": Temp,
        "ClearnessIndex": Clear,
        "Precip_mm_per_day": Precip,
        "tilt_x_GHI": tilt * GHI,
        "temp_sq": Temp ** 2,
        "clear_x_tiltcos": Clear * tilt_cos,
        "precip_x_clear": Precip * (1.0 - Clear),
        "BuildingType": building_type,
    }

    X = pd.DataFrame([feats])
    X["BuildingType"] = pd.Categorical(X["BuildingType"], categories=building_categories)
    X_enc = X.copy()
    X_enc["BuildingType"] = X_enc["BuildingType"].cat.codes

    # --- Load models only when needed (cached afterward) ---
    lgb_models = load_model("lgb_models")
    xgb_models = load_model("xgb_models")
    rf_models  = load_model("rf_models")
    et_models  = load_model("et_models")
    meta_model = load_model("meta_model")

    # --- Generate predictions from each model ---
    pred_lgb = np.mean([np.expm1(m.predict(X)) for m in lgb_models], axis=0)
    pred_xgb = np.mean([np.expm1(m.predict(X_enc)) for m in xgb_models], axis=0)
    pred_rf  = np.expm1(rf_models[0].predict(X_enc))
    pred_et  = np.expm1(et_models[0].predict(X_enc))

    # --- Meta prediction (Ridge ensemble) ---
    meta_X = np.column_stack([pred_lgb, pred_xgb, pred_rf, pred_et])
    pred_final = meta_model.predict(meta_X)[0]

    return round(float(pred_final), 3)

# === Optional: quick test ===
if __name__ == "__main__":
    print("\n🔸 Running test prediction ...")
    result = predict_energy("Accra", "commercial", 20)
    print(f"☀️  Predicted Solar Potential: {result} kWh/m²/year\n")
