# HCAI

## Basic setup

``` bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

``` bash
# Generate mean_plan dataset
python -m src.scripts.dataset

# Run the desired generation file
python -m src.main

# Run UI
python -m streamlit run src/UI.py

# Run UI without opening in browser
python -m streamlit run src/UI.py --server.headless true

```

## Files

* Dataset: [Epi Recipes](https://www.kaggle.com/datasets/hugodarwood/epirecipes?resource=download)
* dataset.py: preprocessing of epi_r.csv and gives meal_dataset.csv
* meal_generation.py: Rag - ⚠️ IGNORE
* meal_generation.py_rag_LLM.py: Rag and LLM
* meal_generation_calorie.py: calorie, fat, protein and sodium
* vectorstore_builder.py: vector embedding and retrieval
