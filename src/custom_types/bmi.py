from openai import BaseModel


class Bmi(BaseModel):
    bmi: float
    bmi_category: str
    base_calorie: int