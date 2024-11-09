from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"
    id = Column(SQLAlchemyUUID, primary_key=True, default=uuid4)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)


users_table = UserTable.__table__


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str

    class Config:
        from_attributes = True

