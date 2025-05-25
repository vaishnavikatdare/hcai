from openai import BaseModel


class UserModel(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    weight: float
    height: float
    diet_preference: str