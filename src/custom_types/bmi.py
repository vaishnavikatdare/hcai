from openai import BaseModel


class BmiRecord(BaseModel):
    bmi: float
    bmi_category: str
    base_calorie: int