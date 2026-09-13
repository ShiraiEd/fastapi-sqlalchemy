from pydantic import BaseModel, ConfigDict

class CreateUser(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str

class UpdateUser(BaseModel):
    name: str | None = None
    email: str | None = None

class UpdateUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None
    email: str | None