# Pipeline: Brain Tumor MRI Classifier

Trains three models on the [Brain Tumor MRI Dataset](.) (Glioma /
Meningioma / Pituitary / No Tumor) — a from-scratch CNN, and transfer-learned
ViT-B/16 and ConvNeXt-Tiny models — and serves predictions from all three
over a small FastAPI service that the `backend` calls.

| Model      | Architecture | Trained how | Route |
|------------|--------------|-------------|-------|
| `cnn`      | `SimpleCNN` (model.py), 4 conv blocks | From scratch (`train.py --model cnn`); `finetune.py` continues an existing checkpoint | `POST /predict` — **the original model** |
| `vit`      | torchvision `vit_b_16` | Transfer-learned from ImageNet weights (`train.py --model vit`) | `POST /predict/vit` |
| `convnext` | torchvision `convnext_tiny` | Transfer-learned from ImageNet weights (`train.py --model convnext`) | `POST /predict/convnext` |

The CNN is small enough to train from random weights on this ~10k-image
dataset. ViT and ConvNeXt are not — see model.py's docstrings for why — so
both start from ImageNet-pretrained weights and fine-tune the whole network
(new classifier head included) at a low learning rate instead.

## Folder contents

| File            | Purpose |
|-----------------|---------|
| `config.py`     | Every hyperparameter, path, and class-name mapping in one place, including the per-model registries (`MODEL_NAMES`, `MODEL_PATHS`, `IMAGE_SIZES`, ...) that the rest of this folder keys off of. |
| `dataset.py`    | Builds the train/val/test `DataLoader`s and image transforms, parametrized by `image_size` (150 for the CNN, 224 for ViT/ConvNeXt). |
| `model.py`      | All three architectures (`build_cnn` / `build_vit` / `build_convnext`) plus `MODEL_BUILDERS`, the name → builder registry shared by training and inference. |
| `train.py`      | Trains any of the three models from scratch (`--model {cnn,vit,convnext}`), saves the best checkpoint, plots accuracy/loss curves. |
| `finetune.py`   | Continues training the **already-trained** `cnn_model.pt` instead of starting over; only overwrites it if it actually improves on the recorded validation accuracy. |
| `evaluate.py`   | Scores a saved checkpoint on the test set (classification report + confusion matrix). Also used internally by `train.py`/`finetune.py`. |
| `inference.py`  | Loads a trained model once per architecture and turns image bytes into a prediction. |
| `api.py`        | FastAPI app exposing `/health`, `/classes`, `/predict`, `/predict/vit`, `/predict/convnext`. |
| `data/`         | Dataset (git-ignored — see root `.gitignore`). Expected layout below. |
| `models/`       | Generated at training time: `{cnn,vit,convnext}_model.pt`, `class_names.json` (shared — same 4 classes for every model), and per-model metrics/plots (`metrics.json`/`training_curves.png`/`confusion_matrix.png` for the CNN, `vit_metrics.json`/`vit_training_curves.png`/... and `convnext_...` for the other two). Unlike `data/`, this folder **is committed to git** — see step 1 — and gets baked into the Docker image at build time — see step 3. |

Expected dataset layout (already present under `pipeline/data/`):

```
pipeline/data/
├── Train/
│   ├── glioma/
│   ├── meningioma/
│   ├── notumor/
│   └── pituitary/
└── Test/
    ├── glioma/
    ├── meningioma/
    ├── notumor/
    └── pituitary/
```

## 1. Train the models (run on your host machine, not in Docker)

The dataset is git-ignored and not baked into the Docker image, so training
happens locally first — a GPU helps a lot here, especially for ViT/ConvNeXt.

```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python train.py --model cnn      # from scratch; add --epochs/--batch-size/--lr to override defaults
python train.py --model vit      # transfer-learned from ImageNet weights (downloaded on first run)
python train.py --model convnext
```

Already have a trained `cnn_model.pt` and just want to nudge it further
instead of starting over?

```bash
python finetune.py               # add --epochs/--lr/--batch-size to override defaults (lr defaults lower than train.py's)
```

`finetune.py` only overwrites `cnn_model.pt` if an epoch actually beats the
validation accuracy already recorded in `metrics.json` — a fine-tuning run
that doesn't help leaves the existing checkpoint untouched rather than
silently shipping a worse model.

Each of these prints per-epoch train/val loss & accuracy, then a final
test-set classification report, and writes to `pipeline/models/` (see the
folder contents table above for exact filenames per model):

- `<model>_model.pt` — the best checkpoint by validation accuracy
- `class_names.json` — index-to-folder-name mapping used at inference time (shared across models)
- metrics/training-curves/confusion-matrix files — best val accuracy / final test accuracy / hyperparameters used, loss & accuracy over epochs, per-class errors on the test set

**Then commit the result:**

```bash
git add pipeline/models
git commit -m "Update trained models"
git push
```

This is the part that's easy to forget coming from other ML projects, where
`models/` is usually git-ignored: here it's tracked on purpose. `pipeline/models/`
is treated as source, not a build artifact, so that a fresh `git clone` (by a
teammate, CI, or a deployment host) already has working trained models in
it — nobody else needs the dataset or a GPU just to build/run the Docker
image. See `pipeline/.gitignore` and step 3 below.

**Exception: `vit_model.pt` and `convnext_model.pt` are NOT committed.** At
~340MB and ~110MB, both are over GitHub's 100MB hard limit on pushed files
(`cnn_model.pt` is fine — ~1.7MB), and the team decided against setting up
Git LFS for this project. `git add pipeline/models` above still works
without extra care — `pipeline/.gitignore` excludes exactly these two files
— but it means those two `.pt` files are shared over Teams instead of git.
**If you're pulling this repo fresh:** grab the current `vit_model.pt` and
`convnext_model.pt` from the team's Teams channel and drop them into
`pipeline/models/` yourself before running `evaluate.py`/`inference.py`/the
API for those two models, or before `docker build`ing — `class_names.json`,
the metrics, and the plots for all three models ARE committed as normal, so
only the two large weight files themselves need to be fetched manually.

Re-check a saved model's accuracy any time without retraining:

```bash
python evaluate.py                     # cnn (default)
python evaluate.py --model vit
python evaluate.py --model convnext
```

### GPU not being used?

`train.py` prints `Using device: cpu` or `Using device: cuda` at startup.
If you expected `cuda` and got `cpu`:

1. **Do you have an NVIDIA GPU?** PyTorch's GPU support (CUDA) only works
   with NVIDIA GPUs. AMD and Intel GPUs (including "integrated graphics")
   aren't supported by CUDA at all — `torch.cuda.is_available()` will
   always be `False` on those, regardless of what you install. A laptop
   with only integrated graphics has no CUDA-capable device to use.

2. **On Windows, plain `pip install -r requirements.txt` gives you a
   CPU-only torch even with an NVIDIA GPU present** — this is the most
   likely reason if you're on Windows. Unlike the Linux wheel (which pulls
   the CUDA runtime in automatically as separate `nvidia-*`/`cuda-*`
   packages), torch's Windows wheel on plain PyPI has no CUDA support built
   in or pulled in. You have to explicitly install from PyTorch's own CUDA
   index instead:
   ```powershell
   pip uninstall torch torchvision
   pip install torch==2.13.0 torchvision==0.28.0 --extra-index-url https://download.pytorch.org/whl/cu130
   ```
   (`--extra-index-url`, not `--index-url` — that keeps PyPI available too,
   so pip can still resolve everything else in `requirements.txt` normally.
   `cu130` matches CUDA 13.0, which the versions pinned above were built
   against; check
   [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/)
   if a newer CUDA index has since replaced it.) On Linux/macOS, the plain
   `pip install -r requirements.txt` from step 1 already does the right
   thing — no extra command needed.

3. **Check which torch build you actually have, on any OS:**
   ```bash
   pip show torch
   ```
   Look at the `Version` line. Something like `2.13.0+cu130` means it's a
   CUDA build; `2.13.0` with no `+` suffix (on Windows) or `2.13.0+cpu`
   means it's CPU-only.

4. **Very new GPU (e.g. RTX 50-series / "Blackwell") + `Using device: cuda`
   printed, but training crashes with `CUDA error: no kernel image is
   available for execution on the device`?** That message means torch
   *found* the GPU but was built before that GPU architecture existed, so
   it has no compiled kernels for it. This bit us during development: we
   originally had `torch==2.3.1` pinned (mid-2024), which predates
   Blackwell/sm_120 entirely. `requirements.txt` is now pinned to a current
   release that supports it. If you're on hardware newer than what's
   pinned right now (PyTorch adds support for each new GPU generation
   shortly after it launches, not before), get the exact matching command
   from
   [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/)
   — pick your OS, Pip, and the newest CUDA version offered.

5. **NVIDIA GPU + correct/current build, still `False`?** Your GPU driver
   is probably too old — update it from NVIDIA's site and re-check with
   `nvidia-smi` in a terminal (if that command isn't recognized at all, the
   driver isn't installed).

## 2. Run the API locally

```bash
uvicorn api:app --reload --port 8001
```

(Port 8001, not 8000 — the backend service owns 8000, so the model service
uses 8001 everywhere: locally, and in Docker below.)

Then, e.g.:

```bash
curl -F "file=@some_scan.jpg" http://localhost:8001/predict
```

## 3. Run via Docker Compose

The trained model is **baked into the Docker image at build time**, not
mounted in at runtime — and because `pipeline/models/` is committed to git
(see step 1), you normally don't need to train anything before doing this.
A plain `git clone` already has a working model in it:

```bash
docker compose -f infra/docker-compose.yml up --build model
```

That's it for the common case. Once built, the image is self-contained:
every future `docker compose up` (without `--build`) starts instantly from
that same baked-in model — no retraining, no dataset, and no volume needed
on whatever machine ends up running the container.

**Producing a genuinely new/better model?** Then the order of operations
matters:

```bash
# 1. Train (writes pipeline/models/cnn_model.pt) -- see step 1 above.
cd pipeline && python train.py

# 2. Commit -- the model is source, not a build artifact.
git add models && git commit -m "Update trained model" && git push
cd ..

# 3. Rebuild. The Dockerfile COPYs the (now-updated) pipeline/models/ into
#    the image here, so this must come after both of the above.
docker compose -f infra/docker-compose.yml up --build model
```

A running container never re-reads `pipeline/models/` off disk, so skipping
step 3 means you keep serving the old model even after training a new one.

**Ports:** the container listens on `8001` and `docker-compose.yml` maps
host `8001` to container `8001` (`"8001:8001"`) — same number on both
sides, deliberately, so there's no mapping to keep track of. From your own
machine's browser/curl once the container is running: `http://localhost:8001`.
From another container on the same compose network (e.g. how `backend`
should call this service): `http://model:8001`, by service name. Either
way it's 8001 — the backend owns 8000, so there's no overlap to worry about.

**Missing/broken model?** `docker build` treats a missing `cnn_model.pt`,
`vit_model.pt`, `convnext_model.pt`, or `class_names.json` as a build
failure (with a clear error message), not something the running service
quietly tolerates — and if a model somehow got past that build check but
not onto disk, the container fails fast on startup instead of serving
broken predictions. See the "Design notes" section below for why. In
practice this means: if you just cloned the repo and haven't yet grabbed
`vit_model.pt`/`convnext_model.pt` from Teams (see step 1's "Exception"
note above), `docker build` will fail with that error — that's expected,
not a bug; go get the two files and try again.

## Running tests

```bash
pip install pytest httpx   # or: pip install -e ".[test]"
pytest
```

Covers the model registries (`config.py`), all three architectures' output
shapes, dataset transforms, `Predictor`/`get_predictor`, `finetune.py`'s
argument parsing and fail-fast behavior, and the API routes. A few tests are
skipped until `vit_model.pt`/`convnext_model.pt` actually exist (see
"Missing/broken model?" above) — they activate automatically once all three
models have been trained.

## API reference

- `GET /health` → `{"status": "ok", "model_loaded": true|false}`
- `GET /classes` → list of `{folder_name, display_name}` for each class
- `POST /predict` — **the original model** (the from-scratch CNN)
- `POST /predict/vit` — the ViT-B/16 model
- `POST /predict/convnext` — the ConvNeXt-Tiny model

All three predict routes take the same request (multipart form, field name
`file`, JPEG/PNG) and return the same response shape:
  ```json
  {
    "predicted_class": "glioma",
    "predicted_label": "Glioma Tumor",
    "confidence": 0.9421,
    "probabilities": {
      "glioma": 0.9421,
      "meningioma": 0.031,
      "notumor": 0.019,
      "pituitary": 0.0079
    }
  }
  ```

## Design notes / learning points

- **Why a separate `model.py`?** Loading saved weights (`state_dict`)
  requires re-creating the *exact* same architecture first. Importing one
  shared class from `model.py` in both `train.py` and `inference.py` means
  they can never drift apart.
- **Why does the CNN train from scratch but ViT/ConvNeXt use pretrained
  ImageNet weights?** With ~9-10k training images across 4 classes, that's
  nowhere near enough data to learn a large transformer's or ConvNeXt's
  weights from random initialization. CNNs like `SimpleCNN` get a strong
  head start "for free" from the convolution operation itself (translation
  equivariance — a learned edge detector works the same wherever it slides
  in the image), which lets them generalize from a modest dataset. ViT in
  particular has no such built-in prior — every patch attends to every
  other patch with no assumption that nearby pixels are related — so
  starting from ImageNet-pretrained weights instead of noise is the
  standard, practical choice at this dataset size. See `model.py`'s
  `build_vit`/`build_convnext` docstrings for more.
- **Why does `MODEL_BUILDERS`/`config.MODEL_NAMES` exist instead of an
  if/elif per script?** Five different files (`train.py`, `finetune.py`,
  `evaluate.py`, `inference.py`, `api.py`) all need to do something
  slightly different per architecture — build it, find its checkpoint,
  pick its image size. Keying all of that off one shared list of names and
  a few dicts in `config.py`/`model.py` means adding a fourth architecture
  later is "add one entry to each dict," not "hunt down every place that
  branches on model name."
- **Why split validation from the Train folder instead of using Test?**
  The Test set is only touched once, at the very end, to get an honest,
  unbiased estimate of real-world accuracy. If you used it during training
  to pick your best checkpoint, you'd be indirectly "leaking" test data into
  your model-selection decisions.
- **Why `state_dict()` instead of saving the whole model?** It's the
  officially recommended PyTorch approach — it's smaller, more portable
  across PyTorch versions, and forces you to keep the architecture
  definition in code (see point 1) rather than pickled inside a binary file.
- **Why does the Docker image contain the trained model but not the
  dataset?** The dataset (huge, git-ignored) is only needed to *produce* a
  model; the running service only needs the *result* of training. Baking
  `pipeline/models/` into the image at build time (via `COPY models/
  ./models/` in the Dockerfile) means a container never has to retrain or
  reach outside itself for weights — spin it up on any machine, or ship the
  built image to a teammate or a deployment server, and it works
  immediately. The cost is that picking up a newly trained model requires
  rebuilding the image, rather than just restarting the container.
- **Why commit `pipeline/models/` to git instead of git-ignoring it like
  most ML projects do?** The usual advice ("don't commit large binaries")
  assumes the model is disposable/regeneratable on demand by whoever needs
  it. Here it isn't: this is a small student-project CNN (not a
  multi-gigabyte pretrained network), and the whole point of baking it into
  the Docker image is that a teammate, CI runner, or grader can build and
  run this service with *zero* dependency on the dataset or a GPU. If the
  model were git-ignored, every one of those would either need to retrain
  from scratch (requiring the ~12k-image dataset none of them may have) or
  rely on a fragile out-of-band way of getting the weights onto their
  machine. Committing it trades a somewhat larger repo for a Docker image
  that always just works from a plain clone.
- **Why does a missing model crash the service instead of degrading
  gracefully (e.g. returning 503s)?** Graceful degradation makes sense when
  "not ready yet" is a normal, temporary state — e.g. a cache still
  warming up. It's the wrong response when the missing thing should
  *always* be there by construction (the model is committed to git and
  copied in at build time — see above) and its absence means the build or
  checkout is actually broken. Silently serving degraded responses in that
  case would hide the real problem (e.g. someone's `.gitignore` swallowed
  `pipeline/models/`, or a shallow/partial clone) behind a vague "service
  unavailable," possibly for a while before anyone notices. Failing fast —
  at `docker build` time via the `RUN test -f ...` check in the Dockerfile,
  and again at container startup via `api.py`'s `warm_up_model()` — surfaces
  that same problem immediately, with a specific error message, at the
  earliest possible point.
