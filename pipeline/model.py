"""
The CNN architecture.

This lives in its own file (separate from train.py) for an important reason:
BOTH training and inference need to build the exact same architecture before
loading saved weights into it. torch.save(model.state_dict()) only saves the
numbers (weights/biases) -- not the architecture -- so whatever code creates
the model at inference time must match the training code exactly. Importing
one shared `SimpleCNN` class from here guarantees that.
"""

import torch.nn as nn

import config


class ConvBlock(nn.Module):
    """
    One "layer" of the CNN: Conv -> BatchNorm -> ReLU -> MaxPool.

    Bundling these four operations into a small reusable block keeps the
    main model definition below short and easy to read, instead of repeating
    the same four lines four times.
    """

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.block = nn.Sequential(
            # padding=1 with a 3x3 kernel keeps the spatial size unchanged;
            # MaxPool2d below is what actually shrinks the feature map.
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            # BatchNorm stabilizes/speeds up training by normalizing the
            # activations flowing between layers.
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),  # halves height and width
        )

    def forward(self, x):
        return self.block(x)


class SimpleCNN(nn.Module):
    """
    A "basic" CNN: four convolutional blocks that progressively extract more
    complex features (edges -> textures -> shapes -> tumor-like regions),
    followed by a small fully-connected classifier head.

    Input:  (batch, 3, IMAGE_SIZE, IMAGE_SIZE)
    Output: (batch, NUM_CLASSES) raw, unnormalized "logits" -- softmax is
            applied later (in inference.py), not inside the model itself.
            This is standard practice because nn.CrossEntropyLoss expects
            raw logits and applies log-softmax internally for you.
    """

    def __init__(self, num_classes: int = config.NUM_CLASSES):
        super().__init__()

        self.features = nn.Sequential(
            ConvBlock(config.NUM_CHANNELS, 32),  # -> 32 x (IMAGE_SIZE/2)^2
            ConvBlock(32, 64),                   # -> 64 x (IMAGE_SIZE/4)^2
            ConvBlock(64, 128),                  # -> 128 x (IMAGE_SIZE/8)^2
            ConvBlock(128, 256),                 # -> 256 x (IMAGE_SIZE/16)^2
        )

        # AdaptiveAvgPool2d(1) squashes each of the 256 feature maps down to
        # a single number, regardless of their exact spatial size. This makes
        # the classifier robust to small changes in IMAGE_SIZE and avoids a
        # huge, overfitting-prone Linear layer hard-coded to one input size.
        self.global_pool = nn.AdaptiveAvgPool2d(1)

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(p=0.3),  # randomly zeroes 30% of activations during
                                 # training only, to reduce overfitting
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.global_pool(x)
        return self.classifier(x)
