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
import torchvision.models as tv_models

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


def build_cnn(num_classes: int = config.NUM_CLASSES, pretrained: bool = True) -> nn.Module:
    """
    Thin wrapper around SimpleCNN so all three architectures share one
    call signature -- see MODEL_BUILDERS below.

    `pretrained` is accepted but ignored: SimpleCNN always trains from
    random initialization (there's no "ImageNet SimpleCNN" to load). The
    parameter exists purely so callers -- train.py, inference.py, and the
    tests -- can call every entry in MODEL_BUILDERS the same way without a
    special case for "cnn".
    """
    return SimpleCNN(num_classes=num_classes)


def build_vit(num_classes: int = config.NUM_CLASSES, pretrained: bool = True) -> nn.Module:
    """
    ViT-B/16, transfer-learned from ImageNet weights.

    Unlike the CNN, this is NOT trained from scratch: with ~9-10k training
    images across 4 classes, there isn't nearly enough data to learn a
    ~86M-parameter transformer's weights from random initialization. CNNs
    have "locality" and "translation equivariance" baked into the
    convolution operation itself (a learned edge detector works the same
    wherever it slides), which acts as a strong prior that lets them
    generalize from modest datasets. A plain ViT has no such built-in
    prior -- every patch attends to every other patch with no assumption
    that nearby pixels are related -- so it typically needs either a huge
    dataset or, as here, pretrained weights to start from a sensible
    representation instead of noise.
    """
    weights = tv_models.ViT_B_16_Weights.DEFAULT if pretrained else None
    vit = tv_models.vit_b_16(weights=weights)

    # torchvision's vit_b_16 ships with `heads` = Sequential(Linear(768, 1000))
    # for ImageNet's 1000 classes. Swap in a fresh head sized for our 4
    # tumor classes; everything before it (the pretrained patch embedding +
    # transformer encoder) is kept and fine-tuned along with the new head.
    in_features = vit.heads.head.in_features
    vit.heads.head = nn.Linear(in_features, num_classes)
    return vit


def build_convnext(num_classes: int = config.NUM_CLASSES, pretrained: bool = True) -> nn.Module:
    """
    ConvNeXt-Tiny, transfer-learned from ImageNet weights.

    ConvNeXt is a modern, still-convolutional architecture (unlike ViT), so
    it keeps the locality/translation-equivariance prior CNNs get "for
    free" -- but it's still a much larger, more capable network than
    SimpleCNN, and its extra capacity is only worth using with a pretrained
    starting point on a dataset this size; trained from scratch it would be
    just as data-starved as the ViT above.
    """
    weights = tv_models.ConvNeXt_Tiny_Weights.DEFAULT if pretrained else None
    convnext = tv_models.convnext_tiny(weights=weights)

    # `classifier` is Sequential(LayerNorm2d, Flatten, Linear(768, 1000));
    # only the final Linear needs replacing to retarget it at our classes.
    in_features = convnext.classifier[-1].in_features
    convnext.classifier[-1] = nn.Linear(in_features, num_classes)
    return convnext


# One builder per architecture, keyed the same way as config.py's path
# dicts -- train.py, inference.py, and api.py all look models up by name
# through this registry instead of branching on the name themselves.
MODEL_BUILDERS = {
    "cnn": build_cnn,
    "vit": build_vit,
    "convnext": build_convnext,
}
