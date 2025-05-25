
import pandas as pd
import shutil
import os
from tools import upload_zip_file
from income_evaluation.utils import get_drive_service, validate_data, get_train_and_test_sets, generate_filename, generate_short_uuid
from autogluon.tabular import TabularPredictor
from sklearn.metrics import classification_report


target_column = 'high_income'
def validate_dataset(income_evaluation_raw: pd.DataFrame) -> pd.DataFrame:
    print('Walidacja danych')

    excepted_number_of_columns = 15

    excepted_names_of_columns = [
        'age', ' workclass', ' fnlwgt', ' education', 
        ' education-num', ' marital-status', ' occupation', 
        ' relationship', ' race', ' sex', ' capital-gain', 
        ' capital-loss', ' hours-per-week', 
        ' native-country', ' income'
        ]


    validate_data(income_evaluation_raw, excepted_number_of_columns, excepted_names_of_columns)

    return income_evaluation_raw



def transform_dataset(income_evaluation_validated: pd.DataFrame) -> pd.DataFrame:
    print('Transfomraja danych')

    income_evaluation_transformed = income_evaluation_validated.copy()

    elminate_spaces_from_column_names(income_evaluation_transformed)
    print('Po usunięciu spacji:')
    print(list(income_evaluation_transformed.columns))

    income_evaluation_transformed = remove_unwanted_columns(income_evaluation_transformed)
    print('Po operacji remove_unwanted_columns:')
    print(list(income_evaluation_transformed.columns))

    income_evaluation_transformed = transform_income_column(income_evaluation_transformed)
    print('Po operacji transform_income_column:')
    print(list(income_evaluation_transformed.columns))
    print(income_evaluation_transformed.head(10))

    income_evaluation_transformed = change_name_of_country_column(income_evaluation_transformed)
    print('Po operacji change_name_of_country_column:')
    print(list(income_evaluation_transformed.columns))

    income_evaluation_transformed = strip_leading_spaces(income_evaluation_transformed)
    print('Po operacji strip_leading_spaces:')
    print(income_evaluation_transformed.head(10))

    replace_question_mark(income_evaluation_transformed)
    print('Po operacji replace_question_mark:')
    print(income_evaluation_transformed.head(10))


    return income_evaluation_transformed


def add_new_features(df):
    # Dodanie nowej kolumny do DataFrame
    df['native_country_grouped'] = df['country_of_birth'].apply(group_native_country)

    print('Po operacji group_native_country:')
    print(df.head(10))
    return df


def train_and_test_sets(income_evaluation_new_features):
    # Podział danych
    X_train, X_test, y_train, y_test = get_train_and_test_sets(income_evaluation_new_features, target_column)

    return X_train, X_test, y_train, y_test


def train_model(X_train, X_test, y_train, y_test):
    print('Trenowanie modelu')

    model_path = "tmp/tabular_model"
    zip_file = 'tmp/tabular_model.zip'

    train_data = pd.concat([X_train, y_train], axis=1)

    predictor = TabularPredictor(label=target_column, path=model_path).fit(train_data=train_data, ag_args_fit={'random_seed': 42})

    predictions = predictor.predict(X_test)

    # Raport klasyfikacji – precyzja, czułość, F1 dla każdej klasy
    report = classification_report(y_test, predictions, digits=4)
    print("Raport klasyfikacji:\n", report)

    shutil.make_archive(base_name=model_path, format='zip', root_dir=model_path)
    print(f"Model spakowany do: {model_path}.zip")
    
    if os.getenv("UPLOAD_MODEL", "false").lower() == "true":
        model_id = generate_short_uuid()

        print(f"Model id : {model_id}")
        upload_zip_file(zip_file, name=generate_filename(base_name='tabular_model', id=model_id), folder_name='models', drive_service=get_drive_service())


def elminate_spaces_from_column_names(data: pd.DataFrame):
    print('Usuwam spacje')

    data.columns = data.columns.str.replace(' ', '', regex=False)


def remove_unwanted_columns(df):
    columns_to_remove = ['capital-loss', 'capital-gain', 'education-num', 'fnlwgt']
    return df.drop(columns=columns_to_remove, errors='ignore')

import pandas as pd

def transform_income_column(df):
    if 'income' in df.columns:
        # Usuwanie spacji z wartości w kolumnie 'income'
        df['income'] = df['income'].str.replace(' ', '', regex=False)
        
        # Zmiana nazwy kolumny na 'high_income'
        df = df.rename(columns={'income': 'high_income'})
        
        # Zamiana tekstowych wartości na logiczne
        df['high_income'] = df['high_income'].map({
            '<=50K': False,
            '>50K': True
        })
    return df

def change_name_of_country_column(df):
    df = df.rename(columns={ 'native-country': 'country_of_birth'})
    return df

def strip_leading_spaces(df):
    # Dla wszystkich kolumn typu tekstowego
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.lstrip()
    return df

def replace_question_mark(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].replace('?', 'Unknown')
    return df

def group_native_country(country):
    latin_america = [
        'Mexico', 'Cuba', 'Jamaica', 'Puerto-Rico', 'Honduras', 'Dominican-Republic',
        'Guatemala', 'Nicaragua', 'El-Salvador', 'Columbia', 'Haiti', 'Trinadad&Tobago',
        'Peru', 'Ecuador'
    ]
    asia = [
        'India', 'China', 'Iran', 'Philippines', 'Vietnam', 'Japan', 'Hong', 'Cambodia',
        'Thailand', 'Laos', 'Taiwan', 'South', 'Outlying-US(Guam-USVI-etc)'
    ]
    europe = [
        'England', 'Germany', 'Italy', 'Poland', 'Portugal', 'France', 'Greece', 'Ireland',
        'Scotland', 'Yugoslavia', 'Hungary', 'Holand-Netherlands'
    ]
    america = ['United-States']

    if country in latin_america:
        return 'Latin America'
    elif country in asia:
        return 'Asia'
    elif country in europe:
        return 'Europe'
    elif country in america:
        return 'America'
    else:
        return 'Other'