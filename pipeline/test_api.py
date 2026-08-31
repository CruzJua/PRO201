"""
Tests for api.py's routes.

Route registration is checked unconditionally (it doesn't need any trained
checkpoint). The actual predict smoke tests need real weights on disk for
ALL THREE models -- api.py's startup event (warm_up_model) deliberately
crashes the whole app if any one model is missing, exactly like the
CNN-only behavior it already had -- so those are skipped until vit/convnext
have been trained too.
"""

import pytest
from fastapi.testclient import TestClient

import config
from api import app

ALL_CHECKPOINTS_EXIST = all(path.exists() for path in config.MODEL_PATHS.values())


def test_predict_routes_are_registered_without_starting_the_app():
    paths = {route.path for route in app.routes}
    assert "/predict" in paths
    assert "/predict/vit" in paths
    assert "/predict/convnext" in paths


def test_predict_stays_the_original_cnn_route():
    # This is the requirement that matters most: /predict must keep serving
    # the original model, not silently become "whichever model was added
    # most recently."
    [predict_route] = [r for r in app.routes if r.path == "/predict"]
    assert "cnn" in predict_route.endpoint.__doc__.lower()


@pytest.mark.skipif(
    not ALL_CHECKPOINTS_EXIST,
    reason="vit/convnext haven't been trained yet -- app startup would crash without all three checkpoints.",
)
@pytest.mark.parametrize("route", ["/predict", "/predict/vit", "/predict/convnext"])
def test_predict_route_smoke(route):
    sample_image = config.TEST_DIR / "glioma" / "1049.jpg"
    with TestClient(app) as client:
        with open(sample_image, "rb") as f:
            response = client.post(route, files={"file": ("scan.jpg", f, "image/jpeg")})

    assert response.status_code == 200
    body = response.json()
    assert body["predicted_class"] in config.CLASS_FOLDER_NAMES
    assert set(body["probabilities"]) == set(config.CLASS_FOLDER_NAMES)


@pytest.mark.skipif(
    not ALL_CHECKPOINTS_EXIST,
    reason="vit/convnext haven't been trained yet -- app startup would crash without all three checkpoints.",
)
def test_health_and_classes_routes():
    with TestClient(app) as client:
        health = client.get("/health")
        classes = client.get("/classes")

    assert health.status_code == 200
    assert health.json()["model_loaded"] is True
    assert classes.status_code == 200
    assert len(classes.json()["classes"]) == config.NUM_CLASSES
