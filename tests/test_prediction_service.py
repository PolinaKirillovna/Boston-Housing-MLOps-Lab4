from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.prediction_service import PredictionService
from db.base import Base
from db.models import PredictionLog, User  # noqa: F401


class DummyModel:
    def predict(self, df):
        return [42.123456]


def test_prediction_service_persists_record(tmp_path, monkeypatch):
    db_file = tmp_path / "service_test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    # создаём пользователя вручную
    from db.models.user import User

    user = User(username="polina", hashed_password="hashed")
    session.add(user)
    session.commit()
    session.refresh(user)

    monkeypatch.setenv("MODEL_VERSION", "unit-test-model")

    service = PredictionService(model=DummyModel(), db_session=session)

    result = service.predict_and_store(
        user_id=user.id,
        features={
            "crim": 0.02729,
            "zn": 0.0,
            "indus": 7.07,
            "chas": 0,
            "nox": 0.469,
            "rm": 7.185,
            "age": 61.1,
            "dis": 4.9671,
            "rad": 2,
            "tax": 242,
            "ptratio": 17.8,
            "black": 392.83,
            "lstat": 4.03,
        },
        source="api",
    )

    assert result["stored"] is True
    assert result["predicted_medv"] == 42.1235
    assert "request_id" in result

    saved = session.query(PredictionLog).filter_by(request_id=result["request_id"]).first()
    assert saved is not None
    assert saved.user_id == user.id
    assert saved.model_version == "unit-test-model"
    assert saved.predicted_medv == 42.1235

    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
