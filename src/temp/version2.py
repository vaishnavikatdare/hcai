# meal plan using BMI and duration
import pandas as pd
import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

DATA_PATH = "/home/vaish/code/hcai/dataset/USDA_Nutrient_Data__Final_View_.csv"
df = pd.read_csv(DATA_PATH)

weight_kg = float(input("Enter your current weight (kg): "))
height_cm = float(input("Enter your height (cm): "))
diet_type = input("Enter diet preference (vegetarian / non-vegetarian): ").strip().lower()

height_m = height_cm / 100
bmi = weight_kg / (height_m ** 2)
min_healthy_weight = 18.5 * height_m ** 2
max_healthy_weight = 24.9 * height_m ** 2

print(f"Your BMI is: {bmi:.1f}")
print(f"Healthy weight range for your height: {min_healthy_weight:.1f} kg – {max_healthy_weight:.1f} kg")

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

goal_days = 0
if goal_type in ["weightloss", "weightgain"]:
    goal_days = int(input(f"In how many days do you want to {goal_type} {target_change_kg} kg? "))

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

goal_phrase = "to maintain current weight"
calorie_target = base_calorie

if goal_type == "weightloss" and goal_days > 0:
    total_deficit = 7700 * target_change_kg
    daily_deficit = total_deficit / goal_days
    calorie_target = max(1200, base_calorie - daily_deficit)
    goal_phrase = f"to lose {target_change_kg} kg in {goal_days} days"
elif goal_type == "weightgain" and goal_days > 0:
    total_surplus = 7700 * target_change_kg
    daily_surplus = total_surplus / goal_days
    calorie_target = base_calorie + daily_surplus
    goal_phrase = f"to gain {target_change_kg} kg in {goal_days} days"

print(f"Goal: {goal_phrase}")
print(f"Final Daily Calorie Target: {int(calorie_target)} kcal")

if diet_type not in ["vegetarian", "non-vegetarian"]:
    print("Invalid input. Please enter 'vegetarian' or 'non-vegetarian'.")
    exit(1)

if diet_type == "vegetarian":
    exclude_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat"]
    df = df[~df["food_category"].str.contains("|".join(exclude_keywords), case=False, na=False)]
else:
    include_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat", "Egg", "Lamb"]
    df = df[df["food_category"].str.contains("|".join(include_keywords), case=False, na=False)]

top_n_foods = 20
grouped = df.groupby("description")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
top_foods = grouped.head(top_n_foods)["description"].tolist()

prompt_text = f"""You are a certified nutritionist. Generate a 1-day {diet_type} meal plan for someone who is {bmi_category.lower()} (BMI: {bmi:.1f}) {goal_phrase}.
Use the following foods: {', '.join(top_foods)}. The plan should contain approximately {int(calorie_target)} kcal and include:
- Breakfast
- Lunch
- Dinner
- 2 snacks
Mention quantities and estimated calories per meal."""

model = OllamaLLM(model="mistral")
prompt = ChatPromptTemplate.from_template(prompt_text)
chain = prompt | model
result = chain.invoke({})

print("=== Generated Meal Plan ===\n")
print(result)

os.makedirs("./outputs/mealplans", exist_ok=True)
goal_label = f"_{goal_type}_{int(target_change_kg)}kg_{goal_days}days" if goal_days > 0 else f"_{goal_type}"
filename = f"./outputs/mealplans/meal_plan_{diet_type.replace('-', '_')}_BMI_{bmi_category.lower()}{goal_label}.txt"
with open(filename, "w") as f:
    f.write(result)
