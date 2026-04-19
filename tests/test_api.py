from fastapi.testclient import TestClient

from app import app
from train import train


client = TestClient(app)


def setup_module(_):
    train()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_setosa():
    response = client.post(
        "/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["class_name"] == "setosa"
