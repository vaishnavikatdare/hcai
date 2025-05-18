from custom_types.bmi import Bmi
from custom_types.target import Target


def get_bmi_data(height_cm: float, weight_kg: float) -> tuple[float, float, float]:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    min_healthy_weight = 18.5 * height_m ** 2
    max_healthy_weight = 24.9 * height_m ** 2

    print(f"Your BMI is: {bmi:.1f}")
    print(f"Healthy weight range for your height: {min_healthy_weight:.1f} kg – {max_healthy_weight:.1f} kg")

    return (bmi, min_healthy_weight, max_healthy_weight)

def get_goal_type(bmi: float, weight_kg: float, min_healthy_weight: float, max_healthy_weight: float) -> tuple[str, float]:
    if bmi < 18.5:
        goal_type = "weightgain"
        target_change_kg = round(min_healthy_weight - weight_kg, 1)
        print(f"Suggested: Gain at least {target_change_kg} kg to reach a healthy BMI.")
    elif bmi > 24.9:
        goal_type = "weightloss"
        target_change_kg = round(weight_kg - max_healthy_weight, 1)
        print(f"Suggested: Lose up to {target_change_kg} kg to reach a healthy BMI.")
    else:
        goal_type = "maintain"
        target_change_kg = 0
        print("Suggested: Maintain your current weight.")

    return (goal_type, target_change_kg)

def get_base_bmi(bmi: float) -> Bmi:
    if bmi < 18.5:
        bmi_category = "Underweight"
        base_calorie = 2600
    elif 18.5 <= bmi < 25:
        bmi_category = "Normal weight"
        base_calorie = 2200
    elif 25 <= bmi < 30:
        bmi_category = "Overweight"
        base_calorie = 1700
    else:
        bmi_category = "Obese"
        base_calorie = 1400

    return Bmi(bmi=bmi, bmi_category=bmi_category, base_calorie=base_calorie)

def get_goal_target(goal_type: str, target_change_kg: float, goal_days: int, bmi: Bmi) -> Target:
    if goal_type == "weightloss" and goal_days > 0:
        total_deficit = 7700 * target_change_kg
        daily_deficit = total_deficit / goal_days
        calorie_target = max(1200, bmi.base_calorie - daily_deficit)
        goal_phrase = f"to lose {target_change_kg} kg in {goal_days} days"
    elif goal_type == "weightgain" and goal_days > 0:
        total_surplus = 7700 * target_change_kg
        daily_surplus = total_surplus / goal_days
        calorie_target = bmi.base_calorie + daily_surplus
        goal_phrase = f"to gain {target_change_kg} kg in {goal_days} days"
    else:
        goal_phrase = "to maintain current weight"
        calorie_target = bmi.base_calorie

    print(f"Goal: {goal_phrase}")
    print(f"Final Daily Calorie Target: {int(calorie_target)} kcal")

    return Target(goal_phrase=goal_phrase, calorie_target=calorie_target)