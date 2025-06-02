from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import logging

from autogluon.tabular import TabularPredictor
from pathlib import Path
from .schemas import IncomeFeatures, PredictionResponse 
from income_evaluation.pipelines.create_model.nodes import group_native_country

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/income",
    tags=["income-evaluation"],
    responses={404: {"description": "Not found"}},
)

# Path to the loaded model
BASE_DIR = Path(__file__).parent.parent.parent
DEFAULT_MODEL_PATH = str(BASE_DIR / "tools" / "unzipped_model")
MODEL_PATH = os.environ.get("MODEL_PATH", DEFAULT_MODEL_PATH)

# Load the predictor only once when the module is imported
try:
    predictor = TabularPredictor.load(MODEL_PATH, require_py_version_match=False)
    logger.info(f"Model loaded successfully. Best model: {predictor.model_best}")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    predictor = None
@router.post("/predict", response_model=PredictionResponse)
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
    
@router.get("/health")
async def health_check():
    """Check if the model is loaded and ready."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": predictor.model_best}