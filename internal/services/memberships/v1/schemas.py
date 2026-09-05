from typing import Optional
from datetime import datetime
from pydantic import BaseModel, model_validator

SKILL_LEVELS = ("white", "red", "purple", "blue")
MEMBERSHIP_TYPES = ("fall", "full", "winter")


class CreateMembershipRequest(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    skill_level: str = "white"
    type: str = "full"
    end_date: datetime
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @model_validator(mode="after")
    def validate_contents(self):
        valid_id = validate_membership_id(self.id)
        if not valid_id:
            raise ValueError(
                "Invalid membership id format. Format should be {10-digit student number}:{school year, e.g 2627}"  # noqa
            )

        if self.skill_level not in SKILL_LEVELS:
            raise ValueError(
                "Invalid skill level. Skill level should be white, red, purple or blue."
            )

        if self.type not in MEMBERSHIP_TYPES:
            raise ValueError(
                "Invalid membership type. Should be fall, winter, or full."
            )

        return self


class UpdateMembershipRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    skill_level: Optional[str] = None
    type: Optional[str] = None
    end_date: Optional[datetime] = None
    updated_at: datetime = datetime.now()

    @model_validator(mode="after")
    def validate_contents(self):
        if self.skill_level and self.skill_level not in SKILL_LEVELS:
            raise ValueError(
                "Invalid skill level. Skill level should be white, red, purple or blue."
            )

        if self.type and self.type not in MEMBERSHIP_TYPES:
            raise ValueError(
                "Invalid membership type. Should be fall, winter, or full."
            )

        return self


def validate_membership_id(membership_id: str) -> bool:
    """
    Returns whether membership_id is valid
    """
    if len(membership_id) != 15 or membership_id[10] != ":":
        return False

    return True
