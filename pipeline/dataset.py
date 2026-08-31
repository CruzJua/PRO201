"""
Data loading utilities.

Keeping this separate from train.py means both train.py AND evaluate.py can
import the exact same transforms/loaders, so we never accidentally evaluate
a model with different preprocessing than it was trained with (a very easy
and very common bug).
"""

import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

import config


def _pil_to_rgb(image):
    """
    Normalizes grayscale AND RGB source images to the same 3-channel format
    so the CNN always receives a consistent input shape, regardless of how a
    given MRI scan was originally saved.

    This has to be a plain, MODULE-LEVEL function rather than a lambda.
    DataLoader(num_workers > 0) spawns separate worker processes and has to
    pickle the Dataset (transforms included) to send it to them. On Windows
    (and on macOS with Python's default "spawn" start method), a lambda
    defined inside another function can't be pickled -- pickle can only
    serialize a function by looking up its module + name, and a lambda's
    name is literally "<lambda>", which doesn't point anywhere reloadable.
    A named top-level function like this one has a real, importable path
    (dataset._pil_to_rgb), so it pickles fine. Forgetting this is a very
    common source of "AttributeError: Can't pickle local object" crashes
    that only show up on Windows/macOS, not Linux (which defaults to the
    "fork" start method and doesn't need to pickle anything).
    """
    return image.convert("RGB")


def build_transforms(image_size: int = config.IMAGE_SIZE):
    """
    Returns (train_transform, eval_transform).

    train_transform includes light data augmentation (random flips/rotation).
    Augmentation is only applied to the TRAINING set — never to validation or
    test data, because we want those to reflect what the model will actually
    see in production, not artificially altered versions.

    image_size is a parameter (not just config.IMAGE_SIZE baked in) because
    the CNN expects 150x150 but ViT/ConvNeXt's pretrained weights expect
    224x224 (config.PRETRAINED_IMAGE_SIZE) -- see config.IMAGE_SIZES.
    """
    to_rgb = transforms.Lambda(_pil_to_rgb)

    train_transform = transforms.Compose([
        to_rgb,
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ToTensor(),  # HWC uint8 [0,255] -> CHW float32 [0,1]
        transforms.Normalize(mean=config.NORMALIZE_MEAN, std=config.NORMALIZE_STD),
    ])

    eval_transform = transforms.Compose([
        to_rgb,
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=config.NORMALIZE_MEAN, std=config.NORMALIZE_STD),
    ])

    return train_transform, eval_transform


def get_dataloaders(image_size: int = config.IMAGE_SIZE, batch_size: int = config.BATCH_SIZE):
    """
    Builds the train / validation / test DataLoaders.

    ImageFolder expects a directory structured as <root>/<class_name>/<image>,
    which is exactly what pipeline/data/Train and pipeline/data/Test already
    look like -- no manual label bookkeeping required.
    """
    train_transform, eval_transform = build_transforms(image_size=image_size)

    # NOTE: ImageFolder applies ONE transform to the whole dataset. We load the
    # training folder twice (once per transform) so that after we split off a
    # validation subset below, the validation half can use the un-augmented
    # eval_transform while the training half keeps augmentation.
    full_train_augmented = datasets.ImageFolder(config.TRAIN_DIR, transform=train_transform)
    full_train_plain = datasets.ImageFolder(config.TRAIN_DIR, transform=eval_transform)

    class_names = full_train_augmented.classes  # alphabetical, e.g. ['glioma', 'meningioma', 'notumor', 'pituitary']
    assert class_names == config.CLASS_FOLDER_NAMES, (
        f"Class folders on disk {class_names} don't match config.CLASS_FOLDER_NAMES "
        f"{config.CLASS_FOLDER_NAMES}. Update config.py if the dataset folder names changed."
    )

    val_size = int(len(full_train_augmented) * config.VAL_SPLIT)
    train_size = len(full_train_augmented) - val_size

    # random_split needs a fixed generator seed so the split is reproducible
    # across runs -- otherwise "accuracy went up" could just mean "got an
    # easier random validation set this time".
    generator = torch.Generator().manual_seed(config.RANDOM_SEED)
    train_indices, val_indices = random_split(
        range(len(full_train_augmented)), [train_size, val_size], generator=generator
    )

    train_dataset = torch.utils.data.Subset(full_train_augmented, train_indices.indices)
    val_dataset = torch.utils.data.Subset(full_train_plain, val_indices.indices)
    test_dataset = datasets.ImageFolder(config.TEST_DIR, transform=eval_transform)

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=config.NUM_WORKERS, pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        num_workers=config.NUM_WORKERS, pin_memory=torch.cuda.is_available(),
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        num_workers=config.NUM_WORKERS, pin_memory=torch.cuda.is_available(),
    )

    return train_loader, val_loader, test_loader, class_names
