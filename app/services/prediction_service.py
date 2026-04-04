import os

import pandas as pd
from sqlalchemy.orm import Session

from db.repositories.prediction_repository import PredictionRepository
from src.train import FEATURE_COLUMNS


class PredictionService:
    """Application service for model inference and persistence."""

    def __init__(self, model, db_session: Session) -> None:
        self.model = model
        self.repository = PredictionRepository(db_session)
        self.model_version = os.getenv("MODEL_VERSION", "1.0.0")

    def predict_and_store(
        self,
        *,
        user_id: int,
        features: dict,
        source: str = "api",
    ) -> dict:
        input_df = pd.DataFrame([features])[FEATURE_COLUMNS]
        prediction = float(self.model.predict(input_df)[0])
        rounded_prediction = round(prediction, 4)

        saved_record = self.repository.save_prediction(
            user_id=user_id,
            features=features,
            predicted_medv=rounded_prediction,
            model_version=self.model_version,
            source=source,
            status="success",
            error_message=None,
        )

        return {
            "request_id": saved_record.request_id,
            "predicted_medv": rounded_prediction,
            "stored": True,
        }
