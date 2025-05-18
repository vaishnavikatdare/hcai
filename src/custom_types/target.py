from openai import BaseModel


class Target(BaseModel):
    goal_phrase: str
    calorie_target: float