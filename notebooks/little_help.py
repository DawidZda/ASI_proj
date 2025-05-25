import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

# Nazwa kolumny zawierającej etykiety klas (0 - brak oszustwa, 1 - oszustwo)
target_column = "FraudFound_P"

def get_train_and_test_sets(data, target_column):
    """
    Dzieli dane wejściowe na zbiór treningowy i testowy w proporcji 80/20.
    """
    X = data.drop(columns=[target_column])
    y = data[target_column]
    return train_test_split(X, y, test_size=0.2, random_state=123)


def get_train_and_test_sets_target_encoded(data, target_column):
    """
    Dzieli dane wejściowe na zbiór treningowy i testowy w proporcji 80/20.
    """
    X = data.drop(columns=[target_column])
    y = data[target_column]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    return train_test_split(X, y_encoded, test_size=0.2, random_state=123)

def get_scores(y_test, y_predictions):
    """
    Oblicza i wyświetla metryki klasyfikacji oraz zwraca je jako słownik.
    """
    accuracy = accuracy_score(y_test, y_predictions)
    precision = precision_score(y_test, y_predictions, average='weighted')
    recall = recall_score(y_test, y_predictions, average='weighted')
    f1 = f1_score(y_test, y_predictions, average='weighted')

    print()
    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1 Score: {f1}")

    return {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    }
def load_csv(file_path):
    """
    Wczytuje plik CSV do pandas DataFrame z obsługą wyjątków.
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Błąd podczas ładowania pliku CSV: {e}")
        raise


def plot_string_column(data, largest, size=20):
    string_columns = data.select_dtypes(include=['object', 'string']).columns.tolist()

    for column_name in string_columns:
        value_counts = data[column_name].value_counts()

        if largest:
            top = value_counts.nlargest(size)
        else: 
            top = value_counts.nsmallest(size)

        top_df = top.reset_index()
        top_df.columns = [column_name, 'count']

        # Wyświetlenie wyników
        sns.barplot(x='count', y=column_name, data=top_df)

        # Dodanie etykiet i wyświetlenie wykresu
        plt.xlabel('Liczba wystąpień')
        plt.ylabel(column_name)
        plt.title(f"Częstotliwość cechy {column_name}")
        plt.show()



def prepare_histograms(data):
    numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
    for column in numeric_columns:
        plt.figure(figsize=(8, 4))
        sns.histplot(data[column], kde=True, bins=30, color='blue')
        plt.title(f'Rozkład cechy {column}')
        plt.show()