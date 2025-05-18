from typing import Literal

from common.bmi import get_base_bmi, get_bmi_data
from custom_types.goal import RecommendedGoal, TargetGoal


def determine_recommended_goal(height_cm: float, weight_kg: float) -> RecommendedGoal:

    (bmi, min_healthy_weight, max_healthy_weight) = get_bmi_data(height_cm, weight_kg)

    goal_type: Literal["weightloss", "weightgain", "maintain"] = "maintain"
    target_change_kg: float = 0.0
    if bmi < 18.5:
        goal_type = "weightgain"
        target_change_kg = round(min_healthy_weight - weight_kg, 1)
        print(f"Suggested: Gain at least {target_change_kg} kg to reach a healthy BMI.")
    elif bmi > 24.9:
        goal_type = "weightloss"
        target_change_kg = round(weight_kg - max_healthy_weight, 1)
        print(f"Suggested: Lose up to {target_change_kg} kg to reach a healthy BMI.")
    else:
        print("Suggested: Maintain your current weight.")

    return RecommendedGoal(
        bmi=bmi,
        goal_type=goal_type,
        target_change_kg=target_change_kg
    )

def calculate_target_goal(recommended_goal: RecommendedGoal, goal_days: int) -> TargetGoal:
    bmi_record = get_base_bmi(recommended_goal.bmi)

    if recommended_goal.goal_type == "weightloss" and goal_days > 0:
        total_deficit = 7700 * recommended_goal.target_change_kg
        daily_deficit = total_deficit / goal_days
        calorie_target = max(1200, bmi_record.base_calorie - daily_deficit)
        goal_phrase = f"to lose {recommended_goal.target_change_kg} kg in {goal_days} days"
    elif recommended_goal.goal_type == "weightgain" and goal_days > 0:
        total_surplus = 7700 * recommended_goal.target_change_kg
        daily_surplus = total_surplus / goal_days
        calorie_target = bmi_record.base_calorie + daily_surplus
        goal_phrase = f"to gain {recommended_goal.target_change_kg} kg in {goal_days} days"
    else:
        goal_phrase = "to maintain current weight"
        calorie_target = bmi_record.base_calorie

    print(f"Goal: {goal_phrase}")
    print(f"Final Daily Calorie Target: {int(calorie_target)} kcal")

    return TargetGoal(
        goal_phrase=goal_phrase,
        calorie_target=calorie_target,
        bmi=bmi_record.bmi,
        bmi_category=bmi_record.bmi_category,
        base_calorie=bmi_record.base_calorie
    )