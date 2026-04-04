"""FastAPI application for Boston Housing price prediction."""

from pathlib import Path
from typing import Dict

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import BASE_DIR, load_config
from src.train import FEATURE_COLUMNS


CONFIG = load_config()
MODEL_PATH = BASE_DIR / CONFIG["paths"]["model_path"]

app = FastAPI(
    title="Boston Housing Prediction API",
    description="API for predicting Boston Housing target variable medv",
    version="1.1.0",
)


class HouseFeatures(BaseModel):
    """Input schema for Boston Housing prediction request."""

    crim: float = Field(..., example=0.02729, description="Per capita crime rate")
    zn: float = Field(..., example=0.0, description="Residential land zoning share")
    indus: float = Field(..., example=7.07, description="Non-retail business acres")
    chas: int = Field(..., example=0, description="Charles River dummy variable")
    nox: float = Field(..., example=0.469, description="Nitric oxides concentration")
    rm: float = Field(..., example=7.185, description="Average number of rooms")
    age: float = Field(..., example=61.1, description="Proportion of old owner units")
    dis: float = Field(..., example=4.9671, description="Distance to employment centers")
    rad: int = Field(..., example=2, description="Accessibility to radial highways")
    tax: int = Field(..., example=242, description="Property tax rate")
    ptratio: float = Field(..., example=17.8, description="Pupil-teacher ratio")
    black: float = Field(..., example=392.83, description="Dataset feature black")
    lstat: float = Field(..., example=4.03, description="Lower status population share")


class PredictionResponse(BaseModel):
    """Output schema for prediction response."""

    predicted_medv: float


def load_model(model_path: Path = MODEL_PATH):
    """Load trained model from disk.

    Args:
        model_path: Path to serialized model file.

    Returns:
        Loaded model object.

    Raises:
        FileNotFoundError: If model artifact does not exist.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}. Run src/train.py first."
        )

    return joblib.load(model_path)


@app.get("/health")
def health_check() -> Dict[str, bool | str]:
    """Return application health status."""
    return {
        "status": "ok",
        "model_exists": MODEL_PATH.exists(),
    }


@app.get("/feature-metadata")
def feature_metadata():
    """Return feature names for frontend integrations."""
    return {
        "features": FEATURE_COLUMNS,
        "target": "medv",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(features: HouseFeatures) -> PredictionResponse:
    """Generate house price prediction for provided features.

    Args:
        features: Validated input payload.

    Returns:
        PredictionResponse with predicted_medv.

    Raises:
        HTTPException: If model is unavailable or prediction fails.
    """
    try:
        model = load_model()
        input_df = pd.DataFrame([features.model_dump()])[FEATURE_COLUMNS]
        prediction = float(model.predict(input_df)[0])
        return PredictionResponse(predicted_medv=round(prediction, 4))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc