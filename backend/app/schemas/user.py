from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    name: str
    # age: int = Field(ge=0, le=130)

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    name: str | None = None
    # age: int | None = Field(ge=0, le=130)

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True