from openai import BaseModel


class Token(BaseModel):
    username: str
    exp: int