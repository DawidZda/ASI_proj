from pydantic import BaseModel, Field

class IncomeFeatures(BaseModel):
    """Input features for income prediction."""
    age: int = Field(..., description="Age of the person", example=39)
    workclass: str = Field(..., description="Work class", example="Private")
    education: str = Field(..., description="Education level", example="Bachelors")
    marital_status: str = Field(..., description="Marital status", example="Married-civ-spouse")
    occupation: str = Field(..., description="Occupation", example="Exec-managerial")
    relationship: str = Field(..., description="Relationship", example="Husband")
    race: str = Field(..., description="Race", example="White")
    sex: str = Field(..., description="Sex", example="Male")
    hours_per_week: int = Field(..., description="Hours per week", example=40)
    country_of_birth: str = Field(..., description="Country of birth", example="United-States")


class PredictionResponse(BaseModel):
    """Response model for prediction."""
    high_income: bool = Field(..., description="Prediction whether income is >50K")
    probability: float = Field(..., description="Probability of high income", example=0.75)