from fastapi import FastAPI

from fastapi import HTTPException
import pandas as pd
import logging
from .schemas import IncomeFeatures, PredictionResponse 
from .predictor import get_predictor

app = FastAPI(title="Income Evaluation API")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

predictor = None

@app.on_event("startup")
def start_app():
    logger.info("Startuję !")
    global predictor
    predictor = get_predictor()


@app.post("/income/predict", response_model=PredictionResponse)
async def predict_income(features: IncomeFeatures):
    """
    Predict if a person's income is greater than 50K based on input features.
    
    Returns a boolean prediction and the probability of the positive class.
    """

    if predictor is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        input_df = pd.DataFrame([features.dict()])

        # Rename columns to match the model's expected format 
        # (required by pydantic standards, you cannot use dash in variable name inside of a request, like "martial-status")
        input_df = input_df.rename(columns={
            "marital_status": "marital-status",
            "hours_per_week": "hours-per-week",
            "country_of_birth": "native-country"
        })

        # KEEP the original country_of_birth column as well
        input_df['country_of_birth'] = input_df['native-country'].copy()

        # Add the missing native_country_grouped column using the imported function
        input_df['native_country_grouped'] = input_df['native-country'].apply(group_native_country)

        # Log the transformed DataFrame for debugging
        logger.info(f"Transformed input: {input_df.columns.tolist()}")

        # Make prediction
        prediction = predictor.predict(input_df)[0]

        # Get probability
        probas = predictor.predict_proba(input_df)
        probability = float(probas.iloc[0][True] if True in probas.columns else 0.0)

        return PredictionResponse(high_income=prediction, probability=round(probability, 3))

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

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