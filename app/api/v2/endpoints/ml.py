from functools import lru_cache
from typing import Literal

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from ml.inference.model_loader import load_model


router = APIRouter(
    prefix="/ml",
    tags=["ML Predictions"],
)


class ChurnPredictionRequest(BaseModel):
    """Validated raw customer features for churn prediction."""

    model_config = ConfigDict(extra="forbid")

    customer_age: int = Field(ge=18, le=75)
    tenure: int = Field(ge=1, le=72)
    monthly_spend: float = Field(ge=500, le=5000)

    contract_type: Literal[
        "monthly", "yearly", "two_year"
    ]

    support_tickets: int = Field(ge=0, le=100)

    usage_frequency: Literal[
        "low", "medium", "high"
    ]

    payment_method: Literal[
        "card", "bank_transfer", "upi", "cash"
    ]


class ChurnPredictionResponse(BaseModel):
    prediction: int
    prediction_label: Literal["not_churn", "churn"]
    churn_probability: float
    model_version: str


MODEL_VERSION = "churn-v1.0.0"


@lru_cache(maxsize=1)
def get_churn_model():
    """Load and cache the verified model once per process."""
    return load_model(MODEL_VERSION)


@router.post(
    "/predict",
    response_model=ChurnPredictionResponse,
)
def predict_churn(
    request: ChurnPredictionRequest,
) -> ChurnPredictionResponse:
    """Predict whether a customer is likely to churn."""

    features = pd.DataFrame(
        [request.model_dump()]
    )

    try:
        model = get_churn_model()

        prediction = int(model.predict(features)[0])

        probabilities = model.predict_proba(features)[0]
        churn_probability = float(probabilities[1])

    except Exception as exc:
        # Keep internal paths and implementation details out of the response.
        raise HTTPException(
            status_code=500,
            detail="Churn prediction is temporarily unavailable.",
        ) from exc

    return ChurnPredictionResponse(
        prediction=prediction,
        prediction_label=(
            "churn" if prediction == 1 else "not_churn"
        ),
        churn_probability=churn_probability,
        model_version=MODEL_VERSION,
    )

