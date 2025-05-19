
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

DATA_PATH = "/home/vaish/code/hcai/dataset/USDA_Nutrient_Data__Final_View_.csv"
df_all = pd.read_csv(DATA_PATH)

meal_types = ["Breakfast", "Lunch", "Snack", "Dinner"]
meal_times = {"Breakfast": (8, 9), "Lunch": (13, 14), "Snack": (16, 17), "Dinner": (19, 20)}

month = 0
continue_loop = True
while continue_loop:
    month += 1
    print(f"\n=== Month {month} Meal Plan Generation ===")

    weight_kg = float(input("Enter your current weight (kg): "))
    height_cm = float(input("Enter your height (cm): "))
    diet_type = input("Enter diet preference (vegetarian / non-vegetarian): ").strip().lower()

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    min_healthy_weight = 18.5 * height_m ** 2
    max_healthy_weight = 24.9 * height_m ** 2

    if bmi < 18.5:
        goal_type = "weightgain"
        goal_weight = min_healthy_weight
        target_change_kg = round(goal_weight - weight_kg, 1)
    elif bmi > 24.9:
        goal_type = "weightloss"
        goal_weight = max_healthy_weight
        target_change_kg = round(weight_kg - goal_weight, 1)
    else:
        goal_type = "maintain"
        goal_weight = weight_kg
        target_change_kg = 0

    bmi_category = "Underweight" if bmi < 18.5 else "Normal weight" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    base_calorie = 2600 if bmi < 18.5 else 2200 if bmi < 25 else 1700 if bmi < 30 else 1400
    calorie_target = base_calorie
    goal_phrase = "to maintain current weight"

    if goal_type in ["weightloss", "weightgain"]:
        print(f"You need to {goal_type.replace('weight', '')} ~{target_change_kg} kg.")
        daily_kcal_change = int(input("Enter your target daily calorie change (e.g. 500, 700, 1000): "))

        total_kcal = 7700 * target_change_kg
        duration_days = total_kcal / daily_kcal_change
        duration_months = duration_days / 30
        duration_months = min(duration_months, 12)

        if goal_type == "weightloss":
            calorie_target = max(1200, base_calorie - daily_kcal_change)
            goal_phrase = f"to lose {target_change_kg} kg in ~{duration_months:.1f} months"
        else:
            calorie_target = base_calorie + daily_kcal_change
            goal_phrase = f"to gain {target_change_kg} kg in ~{duration_months:.1f} months"

    print(f"BMI: {bmi:.1f} ({bmi_category})")
    print(f"Healthy weight range: {min_healthy_weight:.1f} kg – {max_healthy_weight:.1f} kg")
    print(f"Target weight: {goal_weight:.1f} kg")
    if goal_type != "maintain":
        print(f"Estimated duration to reach target weight: {duration_days:.0f} days ({duration_months:.1f} months)")

    df = df_all.copy()
    if diet_type == "vegetarian":
        exclude_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat"]
        df = df[~df["food_category"].str.contains("|".join(exclude_keywords), case=False, na=False)]
    else:
        include_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat", "Egg", "Lamb"]
        df = df[df["food_category"].str.contains("|".join(include_keywords), case=False, na=False)]

    top_foods = df.groupby("description")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
    meal_options = top_foods["description"].tolist()[:28]

    prompt_text = f"""You are a certified nutritionist. Generate a 1-day {diet_type} meal plan for someone who is {bmi_category.lower()} (BMI: {bmi:.1f}) {goal_phrase}.
Use the following foods: {', '.join(meal_options[:20])}. The plan should contain approximately {int(calorie_target)} kcal and include:
- Breakfast
- Lunch
- Dinner
- 2 snacks
Mention quantities and estimated calories per meal."""

    model = OllamaLLM(model="mistral")
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | model
    meal_plan = chain.invoke({})
    print("\n=== Generated Meal Plan ===\n")
    print(meal_plan)

    pdf_path = f"gantt_charts_month_{month}.pdf"
    with PdfPages(pdf_path) as pdf:
            for week in range(4):
                print(f"\nGenerating Gantt chart for Week {week + 1}")
                week_start = datetime.today() + timedelta(days=week * 7)
                gantt_data = []

                for day in range(7):
                    date = week_start + timedelta(days=day)
                    for i, meal in enumerate(meal_types):
                        meal_name = meal_options[(week * 7 + day + i) % len(meal_options)]
                        start_hour, end_hour = meal_times[meal]
                        gantt_data.append({
                            "Meal": f"{meal}: {meal_name}",
                            "Start": date + timedelta(hours=start_hour),
                            "End": date + timedelta(hours=end_hour)
                        })

                df_gantt = pd.DataFrame(gantt_data)
                fig, ax = plt.subplots(figsize=(14, 6))
                for _, row in df_gantt.iterrows():
                    ax.barh(row["Meal"], (row["End"] - row["Start"]).total_seconds() / 3600,
                            left=row["Start"], height=0.4)

                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%a\n%b %d'))
                plt.title(f"Week {week + 1} Gantt Chart – Month {month}")
                pdf.savefig(fig)
                plt.close(fig)
                plt.xlabel("Time")
                plt.ylabel("Meals")
                plt.grid(True)
                plt.tight_layout()

    response = input("Do you want to continue to the next month? (yes / no): ").strip().lower()
    if response != "yes":
        print("Exiting program. Stay healthy!")
        break
