
from src.common.bmi import calculate_bmi, calculate_weight_change_and_goal, estimate_duration
from src.custom_types.goal import TargetGoal

def get_target_goal(height: float, weight: float) -> TargetGoal:
    bmi = calculate_bmi(weight, height)
    goal, change = calculate_weight_change_and_goal(weight, bmi, height)
    duration = estimate_duration(change, goal)

    print(f"\nBMI: {bmi}")
    print(f"Goal: {goal} {f'{change} kg' if change else ''}")
    print(f"Estimated duration: {duration} months" if duration else "You're in a healthy range.")

    return TargetGoal(
        bmi=bmi,
        goal=goal,
        change=change,
        duration=duration
    )
