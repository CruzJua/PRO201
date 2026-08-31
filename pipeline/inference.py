"""
Everything the FastAPI service needs to turn "raw image bytes" into "a
prediction", kept separate from api.py so the ML logic can be unit-tested
or reused without spinning up a web server.
"""

import io
import json
from functools import lru_cache

import torch
import torch.nn.functional as F
from PIL import Image, UnidentifiedImageError

import config
from dataset import build_transforms
from model import MODEL_BUILDERS


class ModelMissingError(RuntimeError):
    """
    Raised when pipeline/models/ doesn't contain a trained model.

    This is NOT an expected/recoverable runtime state. The model is trained
    once, committed to git, and baked into the Docker image at build time
    (see the Dockerfile and pipeline/README.md) -- so by the time this code
    runs, cnn_model.pt and class_names.json should always be there. If
    they're not, the repo or image is broken (e.g. someone forgot to `git
    add pipeline/models` after training, or built from a stale checkout),
    and the right response is to fail loudly and immediately rather than
    limp along -- see get_predictor()'s docstring for how that plays out.
    """


class InvalidImageError(ValueError):
    """Raised when the uploaded bytes aren't a readable image."""


class Predictor:
    """
    Thin wrapper around a trained model that the API calls into.

    We load the model weights ONCE per architecture (see get_predictor()
    below) and reuse the same in-memory model for every request, instead of
    reloading it from disk on every /predict call, which would be slow and
    wasteful.
    """

    def __init__(self, model_name: str = "cnn"):
        if model_name not in config.MODEL_NAMES:
            raise ValueError(
                f"Unknown model_name '{model_name}'. Expected one of {config.MODEL_NAMES}."
            )

        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model_path = config.MODEL_PATHS[model_name]
        if not model_path.exists() or not config.CLASS_NAMES_PATH.exists():
            raise ModelMissingError(
                f"Trained '{model_name}' model not found at {model_path}. "
                "pipeline/models/ is committed to git and baked into the "
                "Docker image at build time, so this should never happen in "
                "a correctly built image or a correctly cloned repo. If "
                f"you're developing locally, run `python train.py --model {model_name}` "
                "(or `python finetune.py` for the cnn) and commit the result. "
                "If you're seeing this in a container, the image was built "
                f"from a checkout that was missing {model_path.name} -- "
                "rebuild from a full clone."
            )

        with open(config.CLASS_NAMES_PATH) as f:
            self.class_names = json.load(f)

        self.model = MODEL_BUILDERS[model_name](num_classes=len(self.class_names), pretrained=False).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()  # disable dropout / use running batchnorm stats

        # Reuse the same eval-time preprocessing that was used for validation
        # and testing during training -- the model was never trained on
        # augmented-looking inputs, so predictions must use the plain
        # transform, sized to whatever this architecture expects (150 for
        # the CNN, 224 for ViT/ConvNeXt -- see config.IMAGE_SIZES).
        _, self.eval_transform = build_transforms(image_size=config.IMAGE_SIZES[model_name])

    def predict(self, image_bytes: bytes) -> dict:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.load()  # force-decode now so corrupt files raise immediately
        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError("Uploaded file is not a valid image.") from exc

        tensor = self.eval_transform(image).unsqueeze(0).to(self.device)  # add batch dim

        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = F.softmax(logits, dim=1).squeeze(0).cpu()

        predicted_index = int(torch.argmax(probabilities).item())
        predicted_folder = self.class_names[predicted_index]

        return {
            "predicted_class": predicted_folder,
            "predicted_label": config.DISPLAY_NAMES.get(predicted_folder, predicted_folder),
            "confidence": float(probabilities[predicted_index]),
            "probabilities": {
                self.class_names[i]: float(probabilities[i])
                for i in range(len(self.class_names))
            },
        }


@lru_cache(maxsize=None)
def get_predictor(model_name: str = "cnn") -> Predictor:
    """
    lru_cache turns this into a lazy singleton PER model_name: the first
    call for a given name builds that Predictor (loading weights from
    disk); every later call with the same name returns that same cached
    instance instantly, instead of re-reading the model off disk on every
    request. maxsize=None is fine here -- model_name only ever takes the
    handful of values in config.MODEL_NAMES, so the cache can't grow
    unbounded.

    api.py calls this once per model at FastAPI startup (not lazily on
    first request) specifically so that a missing model -- raising
    ModelMissingError -- crashes the container immediately with a clear
    error in the logs, instead of the service starting up "successfully"
    and only failing once the first real request for that model comes in.
    """
    return Predictor(model_name)
