from pandas import DataFrame
from common.ollama import get_model_response
from custom_types.goal import TargetGoal


def generate_meal_plan(
    df: DataFrame,
    diet_type: str,
    target: TargetGoal
) -> str:
    if diet_type == "vegetarian":
        exclude_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat"]
        df = df[~df["food_category"].str.contains("|".join(exclude_keywords), case=False, na=False)]
    else:
        include_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat", "Egg", "Lamb"]
        df = df[df["food_category"].str.contains("|".join(include_keywords), case=False, na=False)]

    top_n_foods = 20
    grouped = df.groupby("description")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
    top_foods = grouped.head(top_n_foods)["description"].tolist()

    prompt_text = f"""You are a certified nutritionist. Generate a 1-day {diet_type} meal plan for someone who is {target.bmi_category.lower()} (BMI: {target.bmi:.1f}) {target.goal_phrase}.
    Use the following foods: {', '.join(top_foods)}. The plan should contain approximately {int(target.calorie_target)} kcal and include:
    - Breakfast
    - Lunch
    - Dinner
    - 2 snacks
    Mention quantities and estimated calories per meal."""

    meal_plan = get_model_response(
        model_name="mistral",
        template=prompt_text,
        verbose=True
    )

    return meal_plan
