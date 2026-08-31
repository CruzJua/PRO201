"""
Tests for the multi-model registry in config.py.

These lock in the "one dict per concern, keyed by model name" contract that
model.py, dataset.py, train.py, inference.py, and api.py all rely on --
if a new model name is ever added, forgetting to register it in one of these
dicts should show up here first, not as a KeyError deep inside training.
"""

import config


def test_model_names_lists_all_three_architectures():
    assert set(config.MODEL_NAMES) == {"cnn", "vit", "convnext"}


def test_every_registry_dict_has_an_entry_per_model_name():
    registries = [
        config.MODEL_PATHS,
        config.METRICS_PATHS,
        config.TRAINING_CURVES_PATHS,
        config.CONFUSION_MATRIX_PATHS,
        config.IMAGE_SIZES,
    ]
    for registry in registries:
        assert set(registry.keys()) == set(config.MODEL_NAMES), registry


def test_registered_paths_all_live_under_models_dir():
    for path in {**config.MODEL_PATHS, **config.METRICS_PATHS}.values():
        assert path.parent == config.MODELS_DIR


def test_cnn_keeps_its_original_paths_for_backward_compatibility():
    # cnn_model.pt / metrics.json are already committed to git under these
    # exact names (see README.md) -- the registry must point at the SAME
    # constants, not new ones, or the existing committed model would
    # silently stop being found.
    assert config.MODEL_PATHS["cnn"] == config.MODEL_PATH
    assert config.METRICS_PATHS["cnn"] == config.METRICS_PATH


def test_pretrained_models_use_224_and_cnn_uses_its_own_image_size():
    assert config.IMAGE_SIZES["cnn"] == config.IMAGE_SIZE
    assert config.IMAGE_SIZES["vit"] == config.PRETRAINED_IMAGE_SIZE
    assert config.IMAGE_SIZES["convnext"] == config.PRETRAINED_IMAGE_SIZE
    assert config.PRETRAINED_IMAGE_SIZE == 224
