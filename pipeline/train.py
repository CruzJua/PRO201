"""
Train one of the brain-tumor MRI classifiers: cnn (from scratch), or vit /
convnext (transfer-learned from ImageNet weights -- see model.py).

Usage:
    python train.py                                    # trains the CNN from scratch
    python train.py --model vit
    python train.py --model convnext
    python train.py --epochs 20 --batch-size 64 --lr 5e-4

Note: to continue training the ALREADY-TRAINED cnn_model.pt instead of
starting over, use finetune.py instead of this script.

What this script does, step by step:
    1. Load the Train/ images (with augmentation) and split off a validation
       set from them; load the Test/ images separately (untouched, unseen).
       Images are resized per config.IMAGE_SIZES[args.model] -- 150x150 for
       the CNN, 224x224 for ViT/ConvNeXt.
    2. Build the chosen architecture from model.py (MODEL_BUILDERS) and
       train it for a number of epochs, tracking loss and accuracy on both
       the training and validation splits each epoch.
    3. Save the best-performing model (by validation accuracy) to disk.
    4. Plot the loss/accuracy curves so you can visually check for
       overfitting (train accuracy climbing while val accuracy plateaus).
    5. Run a final evaluation on the held-out Test set and print/save a
       classification report + confusion matrix.
"""

import argparse
import json
import time

import matplotlib
matplotlib.use("Agg")  # write plots to files instead of trying to open a GUI window
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim

import config
from dataset import get_dataloaders
from evaluate import evaluate_model
from model import MODEL_BUILDERS

# vit/convnext start from ImageNet-pretrained weights (see model.py), not
# random initialization like the CNN -- they converge in far fewer epochs
# and need a much smaller LR, since a large LR would wreck the pretrained
# weights before the new classifier head has a chance to adapt to them.
# These are only used when the user doesn't pass --epochs/--lr explicitly
# (see parse_args below), so the CNN's own defaults in config.py are
# untouched.
DEFAULT_EPOCHS = {"cnn": config.NUM_EPOCHS, "vit": 6, "convnext": 6}
DEFAULT_LR = {"cnn": config.LEARNING_RATE, "vit": 1e-4, "convnext": 1e-4}


def parse_args(argv=None):
    """
    argv=None (the default) makes this fall back to sys.argv, i.e. normal
    CLI behavior. Tests pass an explicit list instead, so they can check
    argument parsing without needing real command-line invocation.
    """
    parser = argparse.ArgumentParser(description="Train one of the brain tumor MRI models.")
    parser.add_argument("--model", choices=config.MODEL_NAMES, default="cnn")
    # epochs/lr default to None here (rather than a fixed number) so main()
    # can tell "user didn't pass this" apart from "user explicitly chose
    # the same value config.py already uses" and fill in the right
    # per-model default from DEFAULT_EPOCHS/DEFAULT_LR above.
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=None)
    args = parser.parse_args(argv)
    if args.epochs is None:
        args.epochs = DEFAULT_EPOCHS[args.model]
    if args.lr is None:
        args.lr = DEFAULT_LR[args.model]
    return args


def run_one_epoch(model, loader, criterion, optimizer, device, train: bool):
    """
    Shared logic for one pass over a DataLoader.

    `train=True` runs the training step (backprop + optimizer.step()).
    `train=False` is used for validation: no gradients are computed, and
    dropout/batchnorm behave in inference mode (see model.train()/eval()
    calls in the training loop below).
    """
    model.train() if train else model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    # torch.no_grad() during validation skips building the computation graph
    # needed for backprop, which saves memory and speeds things up since we
    # never call .backward() in this branch.
    context = torch.enable_grad() if train else torch.no_grad()

    with context:
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            if train:
                optimizer.zero_grad()  # clear gradients from the previous batch

            outputs = model(images)          # raw logits, shape (batch, NUM_CLASSES)
            loss = criterion(outputs, labels)

            if train:
                loss.backward()   # compute gradients
                optimizer.step()  # update weights

            running_loss += loss.item() * images.size(0)
            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_accuracy = correct / total
    return epoch_loss, epoch_accuracy


def plot_training_curves(history, output_path=config.TRAINING_CURVES_PATH):
    epochs_range = range(1, len(history["train_loss"]) + 1)

    fig, (ax_loss, ax_acc) = plt.subplots(1, 2, figsize=(12, 5))

    ax_loss.plot(epochs_range, history["train_loss"], label="Train")
    ax_loss.plot(epochs_range, history["val_loss"], label="Validation")
    ax_loss.set_title("Loss")
    ax_loss.set_xlabel("Epoch")
    ax_loss.legend()

    ax_acc.plot(epochs_range, history["train_acc"], label="Train")
    ax_acc.plot(epochs_range, history["val_acc"], label="Validation")
    ax_acc.set_title("Accuracy")
    ax_acc.set_xlabel("Epoch")
    ax_acc.legend()

    fig.tight_layout()
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved training curves to {output_path}")


def main(argv=None):
    args = parse_args(argv)
    torch.manual_seed(config.RANDOM_SEED)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    if device.type == "cpu":
        # torch.cuda.is_available() being False almost always means one of:
        #  (a) no NVIDIA GPU in this machine (AMD/Intel GPUs aren't supported
        #      by CUDA at all), (b) an outdated/missing NVIDIA driver, or
        #  (c) a CPU-only build of torch got installed instead of a CUDA
        #      build (e.g. `pip install torch` resolved a "+cpu" wheel).
        # `pip show torch` prints a Version like "2.3.1+cu121" (has CUDA) or
        # "2.3.1+cpu" (doesn't) -- that's the fastest way to tell (b) apart
        # from (c). See pipeline/README.md's GPU troubleshooting section.
        print("  -> No CUDA GPU detected; training will run on CPU (slower). "
              "See pipeline/README.md if you expected to use a GPU here.")

    # Every path/size below is looked up by args.model through config.py's
    # registries (see config.py's MODEL_NAMES section) instead of branching
    # on the model name here, so cnn/vit/convnext all flow through the same
    # training loop.
    model_path = config.MODEL_PATHS[args.model]
    metrics_path = config.METRICS_PATHS[args.model]
    curves_path = config.TRAINING_CURVES_PATHS[args.model]
    confusion_matrix_path = config.CONFUSION_MATRIX_PATHS[args.model]
    image_size = config.IMAGE_SIZES[args.model]

    train_loader, val_loader, test_loader, class_names = get_dataloaders(
        image_size=image_size, batch_size=args.batch_size
    )
    print(f"Model: {args.model} | Image size: {image_size}")
    print(f"Train batches: {len(train_loader)} | Val batches: {len(val_loader)} | "
          f"Test batches: {len(test_loader)}")
    print(f"Classes (index order): {class_names}")

    model = MODEL_BUILDERS[args.model](num_classes=len(class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    # Start below any possible accuracy (0.0 is a valid, if bad, accuracy) so
    # the very first epoch always saves a checkpoint. Without this, an
    # unlucky/degenerate first epoch that scores exactly 0.0 val accuracy
    # would never satisfy `val_acc > best_val_accuracy` and no model would
    # ever be saved -- crashing the final test-evaluation step below.
    best_val_accuracy = -1.0

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        start = time.time()

        train_loss, train_acc = run_one_epoch(model, train_loader, criterion, optimizer, device, train=True)
        val_loss, val_acc = run_one_epoch(model, val_loader, criterion, optimizer, device, train=False)

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        elapsed = time.time() - start
        print(f"Epoch {epoch:>2}/{args.epochs} | "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f} | {elapsed:.1f}s")

        # Only keep the checkpoint that did best on validation data -- this
        # protects against saving an over-trained model from the final epoch
        # if accuracy happened to dip right at the end.
        if val_acc > best_val_accuracy:
            best_val_accuracy = val_acc
            torch.save(model.state_dict(), model_path)
            print(f"  -> New best model saved (val_acc={val_acc:.4f})")

    plot_training_curves(history, output_path=curves_path)

    # Reload the best checkpoint (not necessarily the last epoch) before the
    # final, held-out test evaluation.
    model.load_state_dict(torch.load(model_path, map_location=device))
    test_accuracy, report, cm = evaluate_model(
        model, test_loader, class_names, device, confusion_matrix_path=confusion_matrix_path
    )

    print("\nFinal test accuracy: {:.2f}%".format(test_accuracy * 100))
    print("\nClassification report:\n", report)

    with open(config.CLASS_NAMES_PATH, "w") as f:
        json.dump(class_names, f, indent=2)

    metrics = {
        "best_val_accuracy": best_val_accuracy,
        "test_accuracy": test_accuracy,
        "epochs_trained": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nSaved model weights to {model_path}")
    print(f"Saved class names to {config.CLASS_NAMES_PATH}")
    print(f"Saved metrics to {metrics_path}")


if __name__ == "__main__":
    main()
