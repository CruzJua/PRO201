"""
Tests for dataset.py's transforms with a parametrized image_size, needed
because the CNN expects 150x150 while ViT/ConvNeXt need 224x224 to match
their pretrained weights.
"""

import numpy as np
import torch
from PIL import Image

import config
from dataset import build_transforms


def _dummy_rgb_image(size=(180, 120)):
    array = np.random.randint(0, 255, (size[1], size[0], 3), dtype=np.uint8)
    return Image.fromarray(array, mode="RGB")


def _dummy_grayscale_image(size=(180, 120)):
    array = np.random.randint(0, 255, (size[1], size[0]), dtype=np.uint8)
    return Image.fromarray(array, mode="L")


def test_default_image_size_matches_config_image_size():
    _, eval_transform = build_transforms()
    tensor = eval_transform(_dummy_rgb_image())
    assert tensor.shape == (config.NUM_CHANNELS, config.IMAGE_SIZE, config.IMAGE_SIZE)


def test_custom_image_size_for_pretrained_models():
    train_transform, eval_transform = build_transforms(image_size=config.PRETRAINED_IMAGE_SIZE)
    for transform in (train_transform, eval_transform):
        tensor = transform(_dummy_rgb_image())
        assert tensor.shape == (
            config.NUM_CHANNELS,
            config.PRETRAINED_IMAGE_SIZE,
            config.PRETRAINED_IMAGE_SIZE,
        )


def test_grayscale_input_is_still_converted_to_three_channels():
    _, eval_transform = build_transforms(image_size=64)
    tensor = eval_transform(_dummy_grayscale_image())
    assert tensor.shape == (3, 64, 64)


def test_eval_transform_is_deterministic_train_transform_is_not_necessarily():
    train_transform, eval_transform = build_transforms(image_size=64)
    image = _dummy_rgb_image()
    first = eval_transform(image)
    second = eval_transform(image)
    assert torch.equal(first, second)
