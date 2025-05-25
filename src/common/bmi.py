def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def healthy_weight_range(height_cm: float) -> tuple[float, float]:
    height_m = height_cm / 100
    return round(18.5 * height_m ** 2, 1), round(24.9 * height_m ** 2, 1)


def calculate_weight_change_and_goal(weight, bmi, height_cm) -> tuple[str, float]:
    min_wt, max_wt = healthy_weight_range(height_cm)
    if bmi < 18.5:
        return "gain", round(min_wt - weight, 1)
    elif bmi > 24.9:
        return "lose", round(weight - max_wt, 1)
    else:
        return "maintain", 0

def estimate_duration(weight_change, goal) -> float:
    if goal == "lose":
        return round(weight_change / 2)
    elif goal == "gain":
        return round(weight_change / 1.5)
    return 0
