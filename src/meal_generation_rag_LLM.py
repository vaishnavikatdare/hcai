# RAG + LLM
import pandas as pd
from datetime import datetime, timedelta
from langchain_ollama import OllamaLLM
from vectorstore_builder import build_vectorstore_from_filtered, setup_rag_chain
import os

meal_df = pd.read_csv("/home/vaish/code/hcai/dataset/meal_dataset.csv")

def filter_meals_by_type_and_calories(diet_type, max_calories=800):
    return meal_df[(meal_df['veg_nonveg'] == diet_type) & (meal_df['calories'] <= max_calories)].dropna(subset=['title']).reset_index(drop=True)

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

def sample_unique_meals_with_context(retriever, model, meal_df, used_meals, allergies, meal_kcal_targets, diet_type):
    meal_data = {}
    for slot in ['breakfast', 'snack1', 'lunch', 'snack2', 'dinner']:
        meal_kcal = meal_kcal_targets.get(slot, 800)
        for _ in range(20):
            query = f"Suggest a {slot} meal suitable for an adult under {meal_kcal} kcal."
            docs = retriever.invoke(query)
            titles = [doc.page_content.strip().split('\n')[0] for doc in docs if doc.page_content.strip() not in used_meals and is_safe(doc.page_content.strip(), allergies)]
            if titles:
                context = "\n".join(titles[:5])
                prompt = (
                    f"You are the best nutritionist. nutritionally balanced, realistic and easy to prepare\n"
                    f"Given these meal titles:\n{context}\n"
                    f"Suggest a personalized {slot} meal under {meal_kcal} kcal. Avoid allergens: {', '.join(allergies)}.\n"
                    "Return only one short title. Do not add Explanation."
                )
                try:
                    response = model.invoke(prompt).strip().split('\n')[0]
                except Exception as e:
                    print(f"LLM error, fallback used. Reason: {e}")
                    response = titles[0]
                used_meals.add(response)
                meal_data[slot] = {"meal": response, "context": [prompt]}
                break
        else:

            fallback_pool = meal_df[
                (meal_df['veg_nonveg'] == diet_type) &
                (~meal_df['title'].isin(used_meals))
            ]
            fallback_pool = fallback_pool[fallback_pool['title'].apply(lambda x: is_safe(x, allergies))]
            if fallback_pool.empty:
                fallback = "No safe fallback meal found"
            else:
                fallback = fallback_pool.sample(1)['title'].values[0]
            used_meals.add(fallback)
            meal_data[slot] = {"meal": fallback, "context": ["fallback"]}
            used_meals.add(fallback)
            meal_data[slot] = {"meal": fallback, "context": ["fallback"]}
    return meal_data

def build_meal_plan_with_rag(start_date, meal_df, retriever, model, allergies, month_csv_path, meal_kcal_targets, diet_type):
    current_date = start_date
    used_meals = set()
    csv_rows = []

    meal_info = (
        meal_df.drop_duplicates(subset="title")
               .set_index("title")[["calories", "protein", "fat", "sodium"]]
               .to_dict("index")
    )

    for day_num in range(28):
        date_str = current_date.strftime('%Y-%m-%d')
        row = {"Date": date_str}
        totals = {"calories": 0, "protein": 0, "fat": 0, "sodium": 0}

        meals = sample_unique_meals_with_context(retriever, model, meal_df, used_meals, allergies, meal_kcal_targets, diet_type)

        for slot, (time, label) in zip(
            ['breakfast', 'snack1', 'lunch', 'snack2', 'dinner'],
            [("08:00", "Breakfast"), ("10:30", "Snack 1"), ("13:00", "Lunch"),
             ("16:00", "Snack 2"), ("19:30", "Dinner")]
        ):
            meal = meals[slot]["meal"]
            row[label] = meal
            row[f"{label} Time"] = time
            macros = meal_info.get(meal, {"calories": 0, "protein": 0, "fat": 0, "sodium": 0})
            row[f"{label} Tags"] = get_tags(macros)
            totals["calories"] += macros["calories"]
            totals["protein"] += macros["protein"]
            totals["fat"] += macros["fat"]
            totals["sodium"] += macros["sodium"]

            if label == "Breakfast":
                print(f"Day {day_num+1} - {date_str}")
            indent = "  " if label == "Snack 1" else "    " if label == "Lunch" else "  " if label == "Snack 2" else "   " if label == "Dinner" else ""
            print(f"{indent}{label} @ {time}: {meal}")

        row.update(totals)
        csv_rows.append(row)
        current_date += timedelta(days=1)

    pd.DataFrame(csv_rows).to_csv(month_csv_path, index=False)
    print(f"\nSaved monthly plan to: {month_csv_path}")

def run_meal_planner():
    start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d")

    weight = float(input("Enter your weight (kg): "))
    height = float(input("Enter your height (cm): "))
    diet_type = input("Enter your diet preference (veg/non-veg): ").strip().lower()
    allergy_input = input("Enter comma-separated allergens to avoid (e.g., nuts,shellfish): ").strip()
    allergies = [a.strip().lower() for a in allergy_input.split(",") if a.strip()]

    bmi = calculate_bmi(weight, height)
    goal, change = calculate_weight_change_and_goal(weight, bmi, height)
    duration = estimate_duration(change, goal)

    print(f"\nBMI: {bmi}")
    print(f"Goal: {goal} {f'{change} kg' if change else ''}")
    print(f"Estimated duration: {duration} months" if duration else "You're in a healthy range.")

    filtered_df = filter_meals_by_type_and_calories(diet_type)
    model = OllamaLLM(model="mistral")
    vectorstore = build_vectorstore_from_filtered(filtered_df, force_rebuild=False)
    retriever = setup_rag_chain(vectorstore)

    meal_kcal_targets = {
        "breakfast": 400,
        "snack1": 150,
        "lunch": 600,
        "snack2": 150,
        "dinner": 600
    }

    month_csv = f"meal_plan_{start_date.strftime('%Y_%m')}.csv"
    build_meal_plan_with_rag(start_date, meal_df, retriever, model, allergies, month_csv, meal_kcal_targets, diet_type)

if __name__ == "__main__":
    run_meal_planner()
