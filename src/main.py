import os

import pandas as pd

from common.bmi import get_base_bmi, get_bmi_data, get_goal_target, get_goal_type
from common.meal_plan import generate_meal_plan


DATA_PATH = os.path.join(os.path.dirname(__file__), "./dataset/USDA_Nutrient_Data__Final_View_.csv")
df = pd.read_csv(DATA_PATH)

weight_kg = float(input("Enter your current weight (kg): "))
height_cm = float(input("Enter your height (cm): "))
diet_type = input("Enter diet preference (vegetarian / non-vegetarian): ").strip().lower()
if diet_type not in ["vegetarian", "non-vegetarian"]:
    print("Invalid input. Please enter 'vegetarian' or 'non-vegetarian'.")
    exit(1)

(bmi, min_healthy_weight, max_healthy_weight) = get_bmi_data(height_cm, weight_kg)

# Get goal type and goal days
(goal_type, target_change_kg) = get_goal_type(bmi, weight_kg, min_healthy_weight, max_healthy_weight)
goal_days = 0
# Get goal days if the goal type is weight loss or gain from user
if goal_type in ["weightloss", "weightgain"]:
    goal_days = int(input(f"In how many days do you want to {goal_type} {target_change_kg} kg? "))

base_bmi = get_base_bmi(bmi)
target = get_goal_target(goal_type, target_change_kg, goal_days, base_bmi)

# Generate meal plan
meal_plan = generate_meal_plan(df, diet_type, base_bmi, target)

os.makedirs("./outputs/mealplans", exist_ok=True)
goal_label = f"_{goal_type}_{int(target_change_kg)}kg_{goal_days}days" if goal_days > 0 else f"_{goal_type}"
filename = f"./outputs/mealplans/meal_plan_{diet_type.replace('-', '_')}_BMI_{base_bmi.bmi_category.lower()}{goal_label}.txt"
with open(filename, "w") as f:
    f.write(meal_plan)
