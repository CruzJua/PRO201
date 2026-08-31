"""
Tests for model.py's three architectures.

vit/convnext builders default to pretrained=True (real usage always wants
ImageNet weights) but accept pretrained=False so tests can build the
architecture without downloading weights or needing network access -- only
the shape/wiring is under test here, not the pretrained weights themselves.
"""

import torch

import config
from model import MODEL_BUILDERS, SimpleCNN, build_cnn, build_convnext, build_vit


def test_model_builders_registry_matches_config_model_names():
    assert set(MODEL_BUILDERS.keys()) == set(config.MODEL_NAMES)


def test_build_cnn_returns_simplecnn_and_correct_output_shape():
    model = build_cnn(num_classes=4)
    assert isinstance(model, SimpleCNN)

    batch = torch.randn(2, config.NUM_CHANNELS, config.IMAGE_SIZE, config.IMAGE_SIZE)
    model.eval()
    with torch.no_grad():
        logits = model(batch)
    assert logits.shape == (2, 4)


def test_build_vit_head_is_replaced_for_num_classes():
    model = build_vit(num_classes=4, pretrained=False)

    batch = torch.randn(2, config.NUM_CHANNELS, config.PRETRAINED_IMAGE_SIZE, config.PRETRAINED_IMAGE_SIZE)
    model.eval()
    with torch.no_grad():
        logits = model(batch)
    assert logits.shape == (2, 4)


def test_build_convnext_head_is_replaced_for_num_classes():
    model = build_convnext(num_classes=4, pretrained=False)

    batch = torch.randn(2, config.NUM_CHANNELS, config.PRETRAINED_IMAGE_SIZE, config.PRETRAINED_IMAGE_SIZE)
    model.eval()
    with torch.no_grad():
        logits = model(batch)
    assert logits.shape == (2, 4)


def test_all_builders_respect_num_classes_via_registry():
    # pretrained=False on every builder, including build_cnn, which ignores
    # the argument -- see build_cnn's docstring for why it still accepts it.
    for name, builder in MODEL_BUILDERS.items():
        model = builder(num_classes=7, pretrained=False)
        image_size = config.IMAGE_SIZES[name]
        batch = torch.randn(1, config.NUM_CHANNELS, image_size, image_size)
        model.eval()
        with torch.no_grad():
            logits = model(batch)
        assert logits.shape == (1, 7), f"model={name}"
