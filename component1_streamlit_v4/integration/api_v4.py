"""
api_v4.py
=========
FastAPI REST Service for Component 1 (Version 4):
Explainable Cognitive Offloading Risk Model (J26-DS-310).

Usage:
------
    uvicorn api_v4:app --host 0.0.0.0 --port 8000
"""

import os
import sys
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.dirname(__file__))
from integration_service_v4 import get_predictor_v4

app = FastAPI(
    title="Explainable Cognitive Offloading Risk Model API (Version 4)",
    version="4.0",
    description="Component 1 REST API for predicting undergraduate cognitive offloading risk with exact LinearSHAP explainability."
)

predictor = get_predictor_v4()


class AssessmentRequest(BaseModel):
    user_inputs: Dict[str, Any]
    top_factors_count: Optional[int] = 5


@app.get("/")
def root():
    return {
        "project": "Explainable Cognitive Offloading Risk Model — J26-DS-310",
        "pipeline_version": "v4_performance_experiments",
        "champion_model": "Calibrated Thresholded Ridge Regressor (Ordinal)",
        "status": "online",
        "selection_protocol": "25-fold Repeated Stratified CV on training split (N=300)",
        "endpoints": ["/health", "/api/v1/predict"]
    }


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": predictor.model is not None}


@app.post("/api/v1/predict")
def predict_risk(request: AssessmentRequest):
    try:
        result = predictor.predict(request.user_inputs, top_factors_count=request.top_factors_count)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")
