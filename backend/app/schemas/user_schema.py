from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str = None
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str = None

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    full_name: str = None
    password: str = None