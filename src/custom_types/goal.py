from openai import BaseModel
from typing import Literal

from custom_types.bmi import BmiRecord

class RecommendedGoal(BaseModel):
    bmi: float
    goal_type: Literal['weightloss', 'weightgain', 'maintain']
    target_change_kg: float

class TargetGoal(BmiRecord):
    goal_phrase: str
    calorie_target: float
