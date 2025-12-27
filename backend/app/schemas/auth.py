from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterIn(BaseModel):
    name: str
    email: str
    password: str

class UserPublic(BaseModel):
    id: int
    name: str
    email: str