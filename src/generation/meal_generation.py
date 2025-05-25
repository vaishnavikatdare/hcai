
import pandas as pd
from datetime import datetime, timedelta
from langchain_ollama import OllamaLLM
from src.common.meal_plan import filter_meals_by_type_and_calories
from src.common.vectorstore_builder import build_vectorstore_from_filtered, setup_rag_chain
import os

meal_df = pd.read_csv("/home/vaish/code/hcai/dataset/meal_dataset.csv")


def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

def healthy_weight_range(height_cm):
    height_m = height_cm / 100
    return round(18.5 * height_m ** 2, 1), round(24.9 * height_m ** 2, 1)

def calculate_weight_change_and_goal(weight, bmi, height_cm):
    min_wt, max_wt = healthy_weight_range(height_cm)
    if bmi < 18.5:
        return "gain", round(min_wt - weight, 1)
    elif bmi > 24.9:
        return "lose", round(weight - max_wt, 1)
    else:
        return "maintain", 0

def estimate_duration(weight_change, goal):
    if goal == "lose":
        return round(weight_change / 2)
    elif goal == "gain":
        return round(weight_change / 1.5)
    return 0

def is_safe(meal_title, allergies):
    return all(allergen.lower() not in meal_title.lower() for allergen in allergies)

def classify_meal(title):
    title = title.lower()
    if any(kw in title for kw in ["soup", "broth", "bisque"]): return "Soup"
    if any(kw in title for kw in ["salad", "slaw"]): return "Salad"
    if any(kw in title for kw in ["snack", "bar", "toast", "bite"]): return "Snack"
    if any(kw in title for kw in ["dessert", "cake", "cookie", "ice cream", "sweet"]): return "Dessert"
    return "Main"

def get_tags(macros):
    tags = []
    if macros.get("protein", 0) > 20: tags.append("High Protein")
    if macros.get("fat", 0) < 10: tags.append("Low Fat")
    if macros.get("sodium", 0) < 300: tags.append("Low Sodium")
    return ", ".join(tags)

def sample_unique_meals_with_context(retriever, meal_df, used_meals, allergies):
    meal_data = {}
    for slot in ['breakfast', 'snack1', 'lunch', 'snack2', 'dinner']:
        for _ in range(20):
            query = f"Suggest a {slot} meal suitable for an adult under 800 kcal."
            docs = retriever.get_relevant_documents(query)
            titles = [doc.page_content.strip() for doc in docs if doc.page_content.strip() not in used_meals and is_safe(doc.page_content.strip(), allergies)]
            if titles:
                selected = titles[0]
                used_meals.add(selected)
                meal_data[slot] = {"meal": selected, "context": titles}
                break
        else:
            fallback = meal_df[~meal_df['title'].isin(used_meals)]['title']
            fallback = fallback[fallback.apply(lambda x: is_safe(x, allergies))].sample(1).values[0]
            used_meals.add(fallback)
            meal_data[slot] = {"meal": fallback, "context": ["fallback"]}
    return meal_data

def build_meal_plan_with_rag(start_date, meal_df, retriever, allergies, month_csv_path):
    current_date = start_date
    used_meals = set()
    csv_rows = []

    meal_info = (
        meal_df.drop_duplicates(subset="title")
               .set_index("title")[["calories", "protein", "fat", "sodium"]]
               .to_dict("index")
    )

    for day_num in range(28):
        meals = sample_unique_meals_with_context(retriever, meal_df, used_meals, allergies)
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"\nDay {day_num+1} - {date_str}")
        row = {"Date": date_str}
        totals = {"calories": 0, "protein": 0, "fat": 0, "sodium": 0}

        for time, slot, label in [
            ("08:00", "breakfast", "Breakfast"),
            ("10:30", "snack1", "Snack 1"),
            ("13:00", "lunch", "Lunch"),
            ("16:00", "snack2", "Snack 2"),
            ("19:30", "dinner", "Dinner")
        ]:
            meal = meals[slot]["meal"]
            context = meals[slot]["context"]
            row[label] = meal
            row[f"{label} Time"] = time
            row[f"{label} Category"] = classify_meal(meal)
            macros = meal_info.get(meal, {"calories": 0, "protein": 0, "fat": 0, "sodium": 0})
            row[f"{label} Tags"] = get_tags(macros)
            totals["calories"] += macros["calories"]
            totals["protein"] += macros["protein"]
            totals["fat"] += macros["fat"]
            totals["sodium"] += macros["sodium"]
            print(f"{label:>9} @ {time}: {meal}")
            # print(f"    RAG Context: {context[:3]}")

        row.update({
            "Total Calories": totals["calories"],
            "Total Protein": totals["protein"],
            "Total Fat": totals["fat"],
            "Total Sodium": totals["sodium"]
        })

        csv_rows.append(row)
        current_date += timedelta(days=1)

    df = pd.DataFrame(csv_rows)
    df.to_csv(month_csv_path, index=False)
    print(f"\nSaved monthly plan to: {month_csv_path}")

def run_meal_planner():
    weight = float(input("Enter your weight (kg): "))
    height = float(input("Enter your height (cm): "))
    diet_type = input("Enter your diet preference (veg/non-veg): ").strip().lower()
    allergy_input = input("Enter comma-separated allergens to avoid (e.g., nuts,shellfish): ").strip()
    allergies = [a.strip().lower() for a in allergy_input.split(",") if a.strip()]
    start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d")

    bmi = calculate_bmi(weight, height)
    goal, change = calculate_weight_change_and_goal(weight, bmi, height)
    duration = estimate_duration(change, goal)

    print(f"\nBMI: {bmi}")
    print(f"Goal: {goal} {f'{change} kg' if change else ''}")
    print(f"Estimated duration: {duration} months" if duration else "You're in a healthy range.")

    filtered_df = filter_meals_by_type_and_calories(meal_df, diet_type)
    model = OllamaLLM(model="mistral")
    vectorstore = build_vectorstore_from_filtered(filtered_df, force_rebuild=False)
    retriever = setup_rag_chain(vectorstore)

    while True:
        month_csv = f"meal_plan_{start_date.strftime('%Y_%m')}.csv"
        build_meal_plan_with_rag(start_date, meal_df, retriever, allergies, month_csv)
        answer = input("\nGenerate meal plan for next month? (yes/no): ").strip().lower()
        if answer != "yes":
            break
        start_date += timedelta(days=30)

run_meal_planner()
