# hcai
hcai project of meal plan generation

# Basic setup Linux
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# Files
dataset.py: preprocessing of epi_r.csv and gives meal_dataset.csv
meal_generation.py: Rag
meal_generation.py_rag_LLM.py: Rag and LLM
vectorstore_builder.py: vector embedding and retrieval

# run
$ python src/meal_generation.py
$ python src/meal_generation_rag_LLM.py
