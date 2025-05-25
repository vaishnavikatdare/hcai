import pandas as pd

from src.common.dataset import get_full_path, read_dataset

def process_dataset() -> None:
    df = read_dataset('epi_r.csv')

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

    output_file_path = get_full_path('meal_dataset.csv')
    df.to_csv(output_file_path, index=False)

    print(df.head())

process_dataset()