import os
import pickle
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


MODEL_PATH = Path(__file__).parent / "model.pkl"
CLASS_NAMES = ["setosa", "versicolor", "virginica"]

app = FastAPI(title="Iris Classifier")


class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


@app.get("/")
def root():
    return {"status": "ok", "environment": os.getenv("APP_ENV", "local")}


@app.post("/predict")
def predict(payload: IrisInput):
    model = load_model()
    features = [[
        payload.sepal_length,
        payload.sepal_width,
        payload.petal_length,
        payload.petal_width,
    ]]
    pred = int(model.predict(features)[0])
    return {"class_id": pred, "class_name": CLASS_NAMES[pred]}
