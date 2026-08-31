"""
FastAPI service that the backend calls to classify a brain MRI image.

Run locally:
    uvicorn api:app --reload --port 8001

(8001, not 8000 -- the backend service owns 8000; see infra/docker-compose.yml.)

Routes:
    GET  /health           -> service status (useful for docker-compose healthchecks)
    GET  /classes          -> the list of classes the model can predict, with display names
    POST /predict          -> the ORIGINAL model (the from-scratch CNN in model.py/train.py)
    POST /predict/vit      -> the ViT-B/16 model (transfer-learned, see model.py)
    POST /predict/convnext -> the ConvNeXt-Tiny model (transfer-learned, see model.py)

All three /predict* routes return the same PredictionResponse shape, so
callers can point at whichever route without changing how they parse the
response.

Every trained model (pipeline/models/) is committed to git and baked into
the Docker image at build time -- none of them are trained or loaded
lazily/optionally by this service. A missing model (any of the three) is
treated as a fatal startup error (see warm_up_model() below), not a
degraded-but-running state.
"""

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from inference import InvalidImageError, get_predictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brain-tumor-model-service")

app = FastAPI(
    title="Brain Tumor MRI Classifier",
    description="Serves predictions from the CNN trained in pipeline/train.py",
    version="1.0.0",
)

# The frontend talks to the backend, and the backend talks to this service --
# but during local development it's common to hit this API directly too, so
# CORS is left open. Tighten `allow_origins` to your real backend URL(s)
# before deploying somewhere public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


class PredictionResponse(BaseModel):
    predicted_class: str
    predicted_label: str
    confidence: float
    probabilities: dict[str, float]


class HealthResponse(BaseModel):
    # Pydantic reserves field names starting with "model_" for its own
    # internals (model_config, model_fields, ...) and warns on startup if a
    # field collides with that "protected namespace". `model_loaded` is the
    # clearest name for this field, so we keep it and just tell Pydantic not
    # to reserve that prefix, rather than renaming the field.
    model_config = {"protected_namespaces": ()}

    status: str
    model_loaded: bool


@app.on_event("startup")
def warm_up_model():
    """
    Load every model into memory as soon as the service starts, instead of
    waiting for each one's first request.

    Deliberately NOT wrapped in try/except: pipeline/models/ is committed to
    git and baked into the image at build time (see the Dockerfile), so a
    missing model here means the image itself was built wrong -- there's no
    valid "running service, some models not loaded yet" state to gracefully
    support. If get_predictor() raises for ANY of the three, we WANT uvicorn
    to crash on startup with that traceback in the logs and the container to
    exit non-zero, so a broken deployment fails immediately and loudly (e.g.
    in CI, or the instant you run `docker compose up`) instead of silently
    serving 503s to real users until someone happens to check /health or
    hits the one route whose model never loaded.
    """
    for model_name in config.MODEL_NAMES:
        get_predictor(model_name)
    logger.info(f"Models loaded successfully at startup: {config.MODEL_NAMES}")


@app.get("/health", response_model=HealthResponse)
def health():
    # If we get here at all, startup already succeeded (see warm_up_model),
    # which means get_predictor() already loaded every model -- there's no
    # "server is up but a model isn't loaded" state to report in this
    # architecture. This still calls get_predictor() for each name (instant:
    # they're cached) rather than hardcoding True, so a future change to the
    # loading strategy can't silently make this endpoint lie.
    for model_name in config.MODEL_NAMES:
        get_predictor(model_name)
    return HealthResponse(status="ok", model_loaded=True)


@app.get("/classes")
def classes():
    return {
        "classes": [
            {"folder_name": name, "display_name": config.DISPLAY_NAMES.get(name, name)}
            for name in config.CLASS_FOLDER_NAMES
        ]
    }


async def _predict_with(model_name: str, file: UploadFile) -> dict:
    """
    Shared body for all three /predict* routes below: validate the upload,
    run it through the named model's Predictor, and translate our own
    exceptions into HTTP errors. Pulled out once instead of copy-pasted
    three times so the validation rules (content type, empty file) can't
    silently drift between routes.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Upload a JPEG or PNG image.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # No try/except around get_predictor() here: if the model weren't
    # loaded, warm_up_model() would have already crashed the app at startup
    # (see above), so this call is always just returning the cached
    # Predictor built when the service came up -- it can't fail at request
    # time in normal operation.
    predictor = get_predictor(model_name)

    try:
        return predictor.predict(image_bytes)
    except InvalidImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """Predictions from the original model: the from-scratch CNN (model.SimpleCNN)."""
    return await _predict_with("cnn", file)


@app.post("/predict/vit", response_model=PredictionResponse)
async def predict_vit(file: UploadFile = File(...)):
    """Predictions from the ViT-B/16 model, transfer-learned from ImageNet weights."""
    return await _predict_with("vit", file)


@app.post("/predict/convnext", response_model=PredictionResponse)
async def predict_convnext(file: UploadFile = File(...)):
    """Predictions from the ConvNeXt-Tiny model, transfer-learned from ImageNet weights."""
    return await _predict_with("convnext", file)
