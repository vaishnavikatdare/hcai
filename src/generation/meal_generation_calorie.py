# RAG + LLM
from datetime import datetime
from langchain_ollama import OllamaLLM
from src.common.dataset import read_dataset
from src.common.goal import get_target_goal
from src.common.meal_plan import build_meal_plan_with_calorie, filter_meals_by_type_and_calories
from src.common.vectorstore_builder import build_vectorstore_from_filtered, setup_rag_chain

meal_df = read_dataset("meal_dataset.csv")


def run_meal_planner():
    start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d")

    weight = float(input("Enter your weight (kg): "))
    height = float(input("Enter your height (cm): "))
    diet_type = input("Enter your diet preference (veg/non-veg): ").strip().lower()
    allergy_input = input("Enter comma-separated allergens to avoid (e.g., nuts,shellfish): ").strip()
    allergies = [a.strip().lower() for a in allergy_input.split(",") if a.strip()]

    target_goal = get_target_goal(height, weight)

    filtered_df = filter_meals_by_type_and_calories(meal_df, diet_type)
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
    build_meal_plan_with_calorie(start_date, meal_df, retriever, model, allergies, month_csv, meal_kcal_targets, diet_type)
