import streamlit as st
import pandas as pd
from datetime import datetime
from langchain_ollama import OllamaLLM
from src.common.dataset import read_dataset
from src.common.goal import get_target_goal
from src.common.meal_plan import build_meal_plan_with_calorie, filter_meals_by_type_and_calories
from src.common.vectorstore_builder import build_vectorstore_from_filtered, setup_rag_chain
from src.constants.defaults import HEIGHT, WEIGHT

# from meal_generation_rag_LLM import (
#     calculate_bmi,
#     calculate_weight_change_and_goal,
#     estimate_duration,
#     filter_meals_by_type_and_calories,
#     build_meal_plan_with_rag,
# )

def ui_page():

    # Input
    st.markdown("### Provide Your Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        weight = st.number_input(
            label=WEIGHT["message"],
            min_value=WEIGHT["min"],
            max_value=WEIGHT["max"],
            step=WEIGHT["step"]
        )
    with col2:
        height = st.number_input(
            label=HEIGHT["message"],
            min_value=HEIGHT["min"],
            max_value=HEIGHT["max"],
            step=HEIGHT["step"]
        )
    with col3:
        start_date = st.date_input("Start Date", datetime.today())

    col4, col5 = st.columns(2)
    with col4:
        diet_type = st.radio(
            "Diet Preference", 
            options=["veg", "non-veg"], 
            format_func=lambda x: "Vegetarian" if x == "veg" else "Non-Vegetarian", 
            horizontal=True
        )
    with col5:
        allergies = st.text_input("Allergies (comma-separated)", "")

    # Generate button
    if st.button("Generate My Plan"):
        allergies_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]
        target_goal = get_target_goal(height, weight)

        st.metric("BMI", f"{target_goal.bmi}")

        bmi_info = """<span style='font-size:16px'>
        <b>BMI Explanation</b><br>
        BMI = weight / height² (in meters)<br>
        Healthy range = 18.5 – 24.9<br>
        <ul style='margin-top:0px'>
        <li>BMI &lt; 18.5 → Underweight</li>
        <li>BMI &gt; 24.9 → Overweight</li>
        <li>18.5 ≤ BMI ≤ 24.9 → Healthy</li>
        </ul>
        </span>"""

        progress_info = """<span style='font-size:16px'>
        <b>📈 Progress Tracker Explanation</b><br>
        Progress is calculated as:<br>
        1 - (kg change remaining / (initial change + estimated duration * daily rate))<br><br>
        This gives you a visual percentage of your journey!
        </span>"""

        with st.expander("ℹ️ BMI & Progress Tracker Info"):
            st.markdown(bmi_info, unsafe_allow_html=True)
            st.markdown(progress_info, unsafe_allow_html=True)

        if target_goal.goal == "gain":
            st.warning(f"Goal: Gain {target_goal.change} kg to reach healthy weight.")
        elif target_goal.goal == "lose":
            st.warning(f"Goal: Lose {target_goal.change} kg to reach healthy weight.")
        else:
            st.success("Goal: Maintain – you're already in a great range!")

        if target_goal.duration:
            progress = 1 - (target_goal.change / (target_goal.change + target_goal.duration * (1.5 if target_goal.goal == "gain" else 2)))
            st.subheader("Progress Tracker")
            st.progress(progress, text=f"{round(progress * 100)}% toward your {target_goal.goal} goal")
        else:
            st.info("No duration needed – you’re already there!")

        meal_df = read_dataset("meal_dataset.csv")
        filtered_df = filter_meals_by_type_and_calories(meal_df, diet_type)
        model = OllamaLLM(model="mistral")
        vectorstore = build_vectorstore_from_filtered(filtered_df, force_rebuild=True)
        retriever = setup_rag_chain(vectorstore)

        meal_kcal_targets = {
            "breakfast": 400,
            "snack1": 150,
            "lunch": 600,
            "snack2": 150,
            "dinner": 600
        }

        csv_name = f"meal_plan_{start_date.strftime('%Y_%m')}.csv"
        build_meal_plan_with_calorie(start_date, meal_df, retriever, model, allergies_list, csv_name, meal_kcal_targets, diet_type)

        df = pd.read_csv(csv_name)
        st.session_state["meal_df"] = df
        st.session_state["csv_name"] = csv_name

    # Display plan if exists
    if "meal_df" in st.session_state:
        df = st.session_state["meal_df"]
        csv_name = st.session_state["csv_name"]

        st.subheader("Your Personalized Meal Plan")
        columns_to_hide = ["calories", "protein", "fat", "sodium"]
        st.dataframe(df.drop(columns=columns_to_hide), use_container_width=True)

        st.download_button(
            label="Download CSV",
            data=open(csv_name, "rb").read(),
            file_name=csv_name,
            mime="text/csv",
            key="main_csv_download"
        )

        st.subheader("📅 View Meals by Day")
        selected_index = st.slider("Select Day", 0, len(df) - 1, 0)
        st.write(f"### Meals for {df.iloc[selected_index]['Date']}")
        for meal_type in ["Breakfast", "Snack 1", "Lunch", "Snack 2", "Dinner"]:
            meal = df.iloc[selected_index][meal_type]
            st.markdown(f"**{meal_type}:** {meal}")

        # Doctor Feedback Section
        st.subheader("🩺 Doctor Feedback on Meal Plan")
        selected_feedback_date = st.selectbox("Select a day to review", df["Date"].unique(), key="doctor_day")

        day_plan = df[df["Date"] == selected_feedback_date].iloc[0]
        for meal_type in ["Breakfast", "Snack 1", "Lunch", "Snack 2", "Dinner"]:
            st.markdown(f"**{meal_type}:** {day_plan[meal_type]}")

        doctor_name = st.text_input("Doctor's Name", key="doctor_name")
        rating = st.slider("Rate this day's meal plan (1 = poor, 5 = excellent)", 1, 5, 3, key="doctor_rating")
        comment = st.text_area("Additional Comments (optional)", key="doctor_comment")

        if st.button("Submit Feedback"):
            feedback = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "doctor": doctor_name,
                "date": selected_feedback_date,
                "rating": rating,
                "comment": comment
            }
            if "feedback_log" not in st.session_state:
                st.session_state["feedback_log"] = []
            st.session_state["feedback_log"].append(feedback)
            st.success("Feedback submitted successfully!")

        if "feedback_log" in st.session_state and st.session_state["feedback_log"]:
            feedback_df = pd.DataFrame(st.session_state["feedback_log"])
            st.download_button(
                label="Download Doctor Feedback CSV",
                data=feedback_df.to_csv(index=False),
                file_name="doctor_feedback.csv",
                mime="text/csv",
                key="feedback_csv_download"
            )
            avg_rating = feedback_df["rating"].mean()
            percentage = round((avg_rating / 5.0) * 100)

            st.subheader("Average Feedback Score")
            st.markdown(f"""
            <div style='width:150px; height:150px; border-radius:75px; background:#4CAF50;
            color:white; display:flex; align-items:center; justify-content:center;
            font-size:32px; margin:auto;'>{percentage}%</div>""", unsafe_allow_html=True)
