import pandas as pd

df = pd.read_csv('/home/vaish/code/hcai/dataset/epi_r.csv')

non_veg_keywords = [
    'chicken', 'beef', 'pork', 'lamb', 'fish', 'shrimp', 'turkey',
    'duck', 'bacon', 'salmon', 'crab', 'ham', 'veal', 'anchovy',
    'mutton', 'tuna', 'meat', 'sausage'
]

def classify_dish(title):
    title_lower = title.lower()
    for keyword in non_veg_keywords:
        if keyword in title_lower:
            return 'non-veg'
    return 'veg'


df['veg_nonveg'] = df['title'].apply(classify_dish)

selected_columns = ['title', 'rating', 'calories', 'protein', 'fat', 'sodium', 'veg_nonveg']
df = df[selected_columns]

df.to_csv('/home/vaish/code/hcai/dataset/meal_dataset.csv', index=False)

print(df.head())
