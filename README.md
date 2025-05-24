# hcai
hcai project of meal plan generation

# Basic setup Linux
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# Files
dataset: https://www.kaggle.com/datasets/hugodarwood/epirecipes?resource=download
dataset.py: preprocessing of epi_r.csv and gives meal_dataset.csv
meal_generation.py: Rag - ignore
meal_generation.py_rag_LLM.py: Rag and LLM
meal_generation_calorie.py: calorie, fat, protein and sodium
vectorstore_builder.py: vector embedding and retrieval

# run
$ python src/meal_generation.py
$ python src/meal_generation_rag_LLM.py
