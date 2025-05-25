from openai import BaseModel

class TargetGoal(BaseModel):
    bmi: float
    goal: str
    change: float
    duration: float
