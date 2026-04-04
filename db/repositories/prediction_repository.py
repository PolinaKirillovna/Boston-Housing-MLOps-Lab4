from db.models.prediction_log import PredictionLog


class PredictionRepository:
    """Repository for prediction log persistence."""

    def __init__(self, db_session) -> None:
        self.db_session = db_session

    def save_prediction(
        self,
        *,
        user_id: int,
        features: dict,
        predicted_medv: float,
        model_version: str,
        source: str,
        status: str,
        error_message: str | None = None,
    ) -> PredictionLog:
        prediction_log = PredictionLog(
            user_id=user_id,
            crim=features["crim"],
            zn=features["zn"],
            indus=features["indus"],
            chas=features["chas"],
            nox=features["nox"],
            rm=features["rm"],
            age=features["age"],
            dis=features["dis"],
            rad=features["rad"],
            tax=features["tax"],
            ptratio=features["ptratio"],
            black=features["black"],
            lstat=features["lstat"],
            predicted_medv=predicted_medv,
            model_version=model_version,
            source=source,
            status=status,
            error_message=error_message,
        )

        self.db_session.add(prediction_log)
        self.db_session.commit()
        self.db_session.refresh(prediction_log)
        return prediction_log

    def get_by_request_id(self, request_id: str) -> PredictionLog | None:
        return (
            self.db_session.query(PredictionLog)
            .filter(PredictionLog.request_id == request_id)
            .first()
        )
