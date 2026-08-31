# Model service image: serves the trained CNN, ViT, and ConvNeXt models over
# FastAPI (see api.py's /predict, /predict/vit, /predict/convnext).
#
# The trained weights (pipeline/models/) are COPIED INTO the image at build
# time below, so all three models are baked into the image itself -- a
# container started from this image loads them once at startup and never
# retrains, even across `docker compose up`/`down`/restarts, and the image
# stays usable if you push it somewhere else (no separate volume required).
#
# pipeline/models/ is committed to git (see pipeline/.gitignore) -- MOSTLY.
# cnn_model.pt is committed like everything else, but vit_model.pt (~340MB)
# and convnext_model.pt (~110MB) are over GitHub's 100MB push limit, and the
# team decided against Git LFS, so those two are git-ignored and shared over
# Teams instead (see pipeline/README.md's "Exception" note). That means a
# fresh `git clone` alone is NOT enough to build this image: you also need
# to manually drop the current vit_model.pt/convnext_model.pt from Teams
# into pipeline/models/ before `docker build` -- see the `RUN test -f ...`
# check below, which fails loudly and specifically if you forget.
#
# You only need to retrain (rather than just fetching from Teams) if you're
# intentionally producing a NEW model:
#   1. (host machine, ideally with a GPU) `pip install -r requirements.txt`, then:
#        python train.py --model cnn        (or `python finetune.py` to continue the existing cnn_model.pt)
#        python train.py --model vit
#        python train.py --model convnext
#      -> writes pipeline/models/{cnn,vit,convnext}_model.pt + class_names.json
#   2. `git add pipeline/models && git commit` -- cnn_model.pt goes through
#      version control like anything else; vit_model.pt/convnext_model.pt
#      are git-ignored (see above), so share the new files over Teams instead
#   3. `docker build -t brain-tumor-model .` (or `docker compose build model`)
#      -> bakes those (now-committed-or-manually-placed) files into this image
#
# A missing model at build time (see the `RUN test -f ...` check below) is
# therefore either a broken checkout/build (for cnn_model.pt) or a "forgot
# to grab it from Teams yet" (for vit/convnext) -- either way, the build
# fails loudly instead of silently shipping an image that will crash every
# container started from it (see api.py).
#
# The training DATASET (pipeline/data/) is still excluded via .dockerignore
# -- it's huge, still git-ignored, and not needed for serving, only
# pipeline/models/ is copied in.

FROM python:3.11-slim

WORKDIR /app

# System deps for Pillow/torch/matplotlib to build & run correctly on slim images.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# CPU-only torch/torchvision wheels are much smaller than the default CUDA
# build and are all this service needs for inference. If you want GPU
# inference in the container, drop this line and let requirements.txt's
# torch/torchvision entries install normally. Keep these versions in sync
# with requirements.txt so the container never loads a state_dict saved by
# a different (and potentially incompatible) torch version than it runs.
RUN pip install --no-cache-dir torch==2.13.0 torchvision==0.28.0 \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Only what the running service actually imports at request time.
# train.py and evaluate.py are dev-only tools (training, and re-scoring a
# saved checkpoint) that nothing here calls -- they stay out of the image
# on purpose, same reasoning as excluding the dataset: no point shipping
# code (or its dependencies) the container will never execute.
COPY config.py model.py dataset.py inference.py api.py ./

# Bake the (committed) trained weights into the image.
COPY models/ ./models/

# Fail the BUILD, loudly and immediately, if any of the three models that
# just got copied in isn't actually there. api.py's startup now loads ALL
# THREE (cnn/vit/convnext -- see config.MODEL_NAMES) and crashes if any one
# is missing, so a broken checkout (e.g. vit_model.pt wasn't committed, or
# someone .gitignore'd it locally) would still produce an image that builds
# "successfully" and only fails later when a container starts (api.py's
# startup crashes -- see there for why) or, worse, when someone finally
# sends a request to the one route whose model never made it in. Catching
# it here instead means `docker build` itself tells you exactly what's
# wrong, at the moment it's wrong, in one line of output.
RUN test -f models/cnn_model.pt && test -f models/vit_model.pt && test -f models/convnext_model.pt \
    && test -f models/class_names.json || \
    (echo "ERROR: one of pipeline/models/{cnn,vit,convnext}_model.pt or class_names.json is missing from the build context." && \
     echo "cnn_model.pt/class_names.json are committed to git -- if those are missing, run 'python train.py --model cnn'" && \
     echo "(or 'python finetune.py') in pipeline/, then 'git add pipeline/models' and commit, and rebuild this image." && \
     echo "vit_model.pt/convnext_model.pt are NOT committed (too large for GitHub) -- grab the current files from" && \
     echo "the team's Teams channel and drop them into pipeline/models/, or train them yourself with 'python train.py --model vit/convnext'." && \
     exit 1)

EXPOSE 8001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
