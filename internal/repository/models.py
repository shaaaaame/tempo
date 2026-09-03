from sqlmodel import Field, SQLModel
from datetime import datetime


class Memberships(SQLModel, table=True):
    id: str = Field(primary_key=True)
    first_name: str
    last_name: str
    email: str
    skill_level: str
    type: str
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
