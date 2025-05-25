# Diet plan and veg non veg input
import pandas as pd
import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

DATA_PATH = "/home/vaish/code/hcai/dataset/USDA_Nutrient_Data__Final_View_.csv"
df = pd.read_csv(DATA_PATH)

diet_type = input("Enter diet preference (vegetarian / non-vegetarian): ").strip().lower()
calorie_target = 2000
top_n_foods = 20

if diet_type not in ["vegetarian", "non-vegetarian"]:
    print("Invalid input. Please enter 'vegetarian' or 'non-vegetarian'.")
    exit(1)

if diet_type == "vegetarian":
    exclude_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat"]
    df = df[~df["food_category"].str.contains("|".join(exclude_keywords), case=False, na=False)]
else:
    include_keywords = ["Beef", "Chicken", "Pork", "Fish", "Turkey", "Meat", "Egg", "Lamb"]
    df = df[df["food_category"].str.contains("|".join(include_keywords), case=False, na=False)]

grouped = df.groupby("description")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
top_foods = grouped.head(top_n_foods)["description"].tolist()

prompt_text = f"""You are a certified nutritionist. Generate a detailed 1-day meal plan using the following foods:
{', '.join(top_foods)}. The meal plan should meet around {calorie_target} kcal, be {diet_type}, and include:
- Breakfast
- Lunch
- Dinner
- 2 snacks
Mention food quantities and estimated calories per meal."""

model = OllamaLLM(model="mistral")
prompt = ChatPromptTemplate.from_template(prompt_text)
chain = prompt | model
result = chain.invoke({})

print("=== Generated Meal Plan ===\n")
print(result)

os.makedirs("./outputs/mealplans", exist_ok=True)

file_name = f"./outputs/mealplans/meal_plan_{diet_type.replace('-', '_')}.txt"
with open(file_name, "w") as f:
    f.write(result)
