from sqlalchemy.orm import Session

from db.models.user import User


class UserRepository:
    """Repository for user persistence and lookup."""

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_by_username(self, username: str) -> User | None:
        return (
            self.db_session.query(User)
            .filter(User.username == username)
            .first()
        )

    def get_by_id(self, user_id: int) -> User | None:
        return (
            self.db_session.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def create_user(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
