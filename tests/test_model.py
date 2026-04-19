from train import train


def test_model_accuracy_above_threshold():
    _, accuracy = train()
    assert accuracy > 0.9, f"Model accuracy too low: {accuracy}"
