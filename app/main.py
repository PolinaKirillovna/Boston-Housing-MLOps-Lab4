"""FastAPI application for Boston Housing price prediction and frontend UI."""

from pathlib import Path
from typing import Any

import joblib
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.auth.security import create_access_token, get_password_hash, verify_password
from app.dependencies.database import get_db
from app.schemas.prediction import (
    DbHealthResponse,
    HealthResponse,
    HouseFeatures,
    PredictionResponse,
)
from app.services.prediction_service import PredictionService
from db.repositories.user_repository import UserRepository
from src.config import BASE_DIR, load_config

CONFIG = load_config()
MODEL_PATH = BASE_DIR / CONFIG["paths"]["model_path"]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Boston Housing Prediction API",
    description="API and web UI for predicting Boston Housing target variable medv",
    version="3.0.0",
)

FEATURE_METADATA = [
    {"name": "crim", "label": "Crime rate", "description": "Per capita crime rate by town.", "placeholder": 0.02729, "type": "float"},
    {"name": "zn", "label": "Residential zoning", "description": "Proportion of residential land zoned for large lots.", "placeholder": 0.0, "type": "float"},
    {"name": "indus", "label": "Business area share", "description": "Proportion of non-retail business acres per town.", "placeholder": 7.07, "type": "float"},
    {"name": "chas", "label": "Near Charles River", "description": "1 if tract bounds river, otherwise 0.", "placeholder": 0, "type": "int"},
    {"name": "nox", "label": "Pollution level", "description": "Nitric oxides concentration.", "placeholder": 0.469, "type": "float"},
    {"name": "rm", "label": "Average rooms", "description": "Average number of rooms per dwelling.", "placeholder": 7.185, "type": "float"},
    {"name": "age", "label": "Old houses share", "description": "Proportion of owner-occupied units built before 1940.", "placeholder": 61.1, "type": "float"},
    {"name": "dis", "label": "Distance to job centers", "description": "Weighted distances to employment centers.", "placeholder": 4.9671, "type": "float"},
    {"name": "rad", "label": "Highway access", "description": "Accessibility index to radial highways.", "placeholder": 2, "type": "int"},
    {"name": "tax", "label": "Property tax", "description": "Full-value property tax rate.", "placeholder": 242, "type": "int"},
    {"name": "ptratio", "label": "Pupil-teacher ratio", "description": "Pupil-teacher ratio by town.", "placeholder": 17.8, "type": "float"},
    {"name": "black", "label": "Dataset feature black", "description": "Original Boston Housing dataset feature kept for reproducibility.", "placeholder": 392.83, "type": "float"},
    {"name": "lstat", "label": "Lower status share", "description": "Percentage of lower status population.", "placeholder": 4.03, "type": "float"},
]


def load_model(model_path: Path = MODEL_PATH) -> Any:
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}. Run training first.")
    return joblib.load(model_path)


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_path)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", model_exists=MODEL_PATH.exists())


@app.get("/db-health", response_model=DbHealthResponse)
def db_health_check(db: Session = Depends(get_db)) -> DbHealthResponse:
    try:
        db.execute(text("SELECT 1"))
        return DbHealthResponse(status="ok", database="reachable")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database is unavailable: {exc}") from exc


@app.get("/feature-metadata")
def feature_metadata() -> dict[str, Any]:
    return {"features": FEATURE_METADATA, "target": "medv"}


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    repository = UserRepository(db)

    existing_user = repository.get_by_username(payload.username)
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already exists")

    created_user = repository.create_user(
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
    )
    return UserResponse(id=created_user.id, username=created_user.username)


@app.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    repository = UserRepository(db)
    user = repository.get_by_username(payload.username)

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)


@app.post("/predict", response_model=PredictionResponse)
def predict(
    features: HouseFeatures,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> PredictionResponse:
    try:
        model = load_model()
        service = PredictionService(model=model, db_session=db)
        result = service.predict_and_store(
            user_id=current_user.id,
            features=features.model_dump(),
            source="api",
        )
        return PredictionResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
