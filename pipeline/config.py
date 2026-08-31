"""
Central place for every "magic number" used by the pipeline.

Good practice: hyperparameters, paths, and other constants should live in
ONE file so you never have to hunt through train.py / api.py / inference.py
to figure out what image size the model expects, or to tweak the learning
rate before a re-run. Everything else in this folder imports from here.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Path(__file__).resolve().parent = the "pipeline/" folder itself, no matter
# what directory you launch the script from. This avoids bugs where a script
# works when run from one folder but breaks when run from another.
PIPELINE_DIR = Path(__file__).resolve().parent

DATA_DIR = PIPELINE_DIR / "data"
TRAIN_DIR = DATA_DIR / "Train"
TEST_DIR = DATA_DIR / "Test"

# Everything the training run produces (weights, plots, metrics) goes here.
# Unlike a lot of ML projects, this folder is deliberately COMMITTED to git
# (see pipeline/.gitignore) rather than ignored: we train once, commit the
# result, and every `docker build` after that bakes in that exact committed
# model (see the Dockerfile) instead of retraining on every image build or
# container start. That means `pipeline/models/cnn_model.pt` and
# `class_names.json` are expected to always exist once you've cloned the
# repo -- if they're missing, that's a broken checkout/build, not a normal
# "not trained yet" state (see inference.py).
MODELS_DIR = PIPELINE_DIR / "models"
MODEL_PATH = MODELS_DIR / "cnn_model.pt"
CLASS_NAMES_PATH = MODELS_DIR / "class_names.json"
METRICS_PATH = MODELS_DIR / "metrics.json"
TRAINING_CURVES_PATH = MODELS_DIR / "training_curves.png"
CONFUSION_MATRIX_PATH = MODELS_DIR / "confusion_matrix.png"

# ViT and ConvNeXt checkpoints/artifacts, named the same way as the CNN's
# above but prefixed so all three can live side by side in models/.
VIT_MODEL_PATH = MODELS_DIR / "vit_model.pt"
VIT_METRICS_PATH = MODELS_DIR / "vit_metrics.json"
VIT_TRAINING_CURVES_PATH = MODELS_DIR / "vit_training_curves.png"
VIT_CONFUSION_MATRIX_PATH = MODELS_DIR / "vit_confusion_matrix.png"

CONVNEXT_MODEL_PATH = MODELS_DIR / "convnext_model.pt"
CONVNEXT_METRICS_PATH = MODELS_DIR / "convnext_metrics.json"
CONVNEXT_TRAINING_CURVES_PATH = MODELS_DIR / "convnext_training_curves.png"
CONVNEXT_CONFUSION_MATRIX_PATH = MODELS_DIR / "convnext_confusion_matrix.png"

# Canonical list of architectures this pipeline supports, plus one dict per
# concern (checkpoint path / metrics / plots / expected input size) keyed by
# that same name. model.py, dataset.py, train.py, inference.py, and api.py
# all key off these dicts instead of each hardcoding its own if/elif chain
# over model names, so adding a fourth architecture later means adding one
# entry to each dict here rather than hunting through five files.
MODEL_NAMES = ["cnn", "vit", "convnext"]

MODEL_PATHS = {"cnn": MODEL_PATH, "vit": VIT_MODEL_PATH, "convnext": CONVNEXT_MODEL_PATH}
METRICS_PATHS = {"cnn": METRICS_PATH, "vit": VIT_METRICS_PATH, "convnext": CONVNEXT_METRICS_PATH}
TRAINING_CURVES_PATHS = {
    "cnn": TRAINING_CURVES_PATH,
    "vit": VIT_TRAINING_CURVES_PATH,
    "convnext": CONVNEXT_TRAINING_CURVES_PATH,
}
CONFUSION_MATRIX_PATHS = {
    "cnn": CONFUSION_MATRIX_PATH,
    "vit": VIT_CONFUSION_MATRIX_PATH,
    "convnext": CONVNEXT_CONFUSION_MATRIX_PATH,
}

# ---------------------------------------------------------------------------
# Data / model hyperparameters
# ---------------------------------------------------------------------------
IMAGE_SIZE = 150          # every image is resized to IMAGE_SIZE x IMAGE_SIZE (the CNN only)
NUM_CHANNELS = 3          # we force everything to RGB, see dataset.py
NUM_CLASSES = 4

# ViT-B/16 and ConvNeXt-Tiny's ImageNet-pretrained weights were trained on
# 224x224 inputs -- ViT's patch embedding and ConvNeXt's downsampling stages
# are both shaped around that exact size, so both must be fed 224x224, not
# IMAGE_SIZE, or the pretrained weights are the wrong shape/scale to be useful.
PRETRAINED_IMAGE_SIZE = 224

# What input size each architecture expects, keyed like the path dicts above.
IMAGE_SIZES = {"cnn": IMAGE_SIZE, "vit": PRETRAINED_IMAGE_SIZE, "convnext": PRETRAINED_IMAGE_SIZE}

BATCH_SIZE = 32
NUM_EPOCHS = 15
LEARNING_RATE = 1e-3
VAL_SPLIT = 0.1           # fraction of the training set held out for validation
RANDOM_SEED = 42
NUM_WORKERS = 2           # DataLoader background processes; 0 is safest on Windows

# ImageNet normalization constants. The CNN trains from scratch, so these are
# just well-tested "center your pixel values around 0" numbers for it -- but
# for ViT/ConvNeXt they matter for a second reason: their pretrained weights
# were themselves trained on inputs normalized with these exact same
# mean/std, so reusing them here isn't a coincidence, it's required.
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]

# Folder names on disk (must match pipeline/data/Train/<name> exactly).
# torchvision.datasets.ImageFolder assigns class indices by sorting these
# alphabetically, so we keep this list sorted to make the mapping obvious.
CLASS_FOLDER_NAMES = ["glioma", "meningioma", "notumor", "pituitary"]

# Human-friendly labels for API responses / plots, keyed by the folder name.
DISPLAY_NAMES = {
    "glioma": "Glioma Tumor",
    "meningioma": "Meningioma Tumor",
    "notumor": "No Tumor (Normal)",
    "pituitary": "Pituitary Tumor",
}
