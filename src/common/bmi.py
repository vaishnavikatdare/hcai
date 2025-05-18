from custom_types.bmi import BmiRecord


def get_bmi_data(height_cm: float, weight_kg: float) -> tuple[float, float, float]:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    min_healthy_weight = 18.5 * height_m ** 2
    max_healthy_weight = 24.9 * height_m ** 2

    print(f"Your BMI is: {bmi:.1f}")
    print(f"Healthy weight range for your height: {min_healthy_weight:.1f} kg – {max_healthy_weight:.1f} kg")

    return (bmi, min_healthy_weight, max_healthy_weight)

def get_base_bmi(bmi: float) -> BmiRecord:
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

    return BmiRecord(bmi=bmi, bmi_category=bmi_category, base_calorie=base_calorie)
