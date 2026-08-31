"""
Tests for inference.py's multi-model Predictor.

get_predictor("cnn") is expected to work right now: cnn_model.pt is already
committed (see README.md's "why commit models/" design note). get_predictor
for "vit"/"convnext" is expected to raise ModelMissingError until those are
actually trained -- that's not a bug, it's the same "fail loudly if the
checkpoint isn't there" behavior the CNN already has, and it's what proves
these tests were written before the checkpoints existed.
"""

import pytest

import config
import inference


@pytest.fixture(autouse=True)
def _clear_predictor_cache():
    inference.get_predictor.cache_clear()
    yield
    inference.get_predictor.cache_clear()


def test_unknown_model_name_raises_value_error():
    with pytest.raises(ValueError):
        inference.get_predictor("not-a-real-model")


def test_cnn_predictor_loads_from_the_committed_checkpoint():
    predictor = inference.get_predictor("cnn")
    assert predictor.class_names == config.CLASS_FOLDER_NAMES


def test_get_predictor_is_cached_per_model_name():
    first = inference.get_predictor("cnn")
    second = inference.get_predictor("cnn")
    assert first is second


@pytest.mark.parametrize("model_name", ["vit", "convnext"])
def test_predictor_raises_model_missing_error_before_training(model_name):
    if config.MODEL_PATHS[model_name].exists():
        pytest.skip(f"{model_name}_model.pt already exists -- this checkpoint has been trained.")
    with pytest.raises(inference.ModelMissingError):
        inference.get_predictor(model_name)


def test_cnn_predict_returns_a_well_formed_result():
    sample_image = config.TEST_DIR / "glioma" / "1049.jpg"
    assert sample_image.exists(), "expected test fixture image is missing from pipeline/data/Test"

    predictor = inference.get_predictor("cnn")
    result = predictor.predict(sample_image.read_bytes())

    assert result["predicted_class"] in config.CLASS_FOLDER_NAMES
    assert 0.0 <= result["confidence"] <= 1.0
    assert set(result["probabilities"]) == set(config.CLASS_FOLDER_NAMES)
    assert abs(sum(result["probabilities"].values()) - 1.0) < 1e-4


def test_predict_rejects_invalid_image_bytes():
    predictor = inference.get_predictor("cnn")
    with pytest.raises(inference.InvalidImageError):
        predictor.predict(b"this is not an image")
