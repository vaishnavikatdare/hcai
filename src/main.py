import os

import pandas as pd

from common.goal import calculate_target_goal, determine_recommended_goal
from common.meal_plan import generate_meal_plan


DATA_PATH = os.path.join(os.path.dirname(__file__), "./dataset/USDA_Nutrient_Data__Final_View_.csv")
df = pd.read_csv(DATA_PATH)

weight_kg = float(input("Enter your current weight (kg): "))
height_cm = float(input("Enter your height (cm): "))
diet_type = input("Enter diet preference (vegetarian / non-vegetarian): ").strip().lower()
if diet_type not in ["vegetarian", "non-vegetarian"]:
    print("Invalid input. Please enter 'vegetarian' or 'non-vegetarian'.")
    exit(1)

# Get goal type and goal days
recommended_goal = determine_recommended_goal(height_cm=height_cm, weight_kg=weight_kg)
goal_days = 0
# Get goal days if the goal type is weight loss or gain from user
if recommended_goal.goal_type in ["weightloss", "weightgain"]:
    goal_days = int(input(f"In how many days do you want to {recommended_goal.goal_type} {recommended_goal.target_change_kg} kg? "))

target = calculate_target_goal(recommended_goal=recommended_goal, goal_days=goal_days)

# Generate meal plan
meal_plan = generate_meal_plan(df, diet_type, target)

os.makedirs("./outputs/mealplans", exist_ok=True)
goal_label = f"_{recommended_goal.goal_type}_{int(recommended_goal.target_change_kg)}kg_{goal_days}days" if goal_days > 0 else f"_{recommended_goal.goal_type}"
filename = f"./outputs/mealplans/meal_plan_{diet_type.replace('-', '_')}_BMI_{target.bmi_category.lower()}{goal_label}.txt"
with open(filename, "w") as f:
    f.write(meal_plan)
