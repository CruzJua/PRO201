"""
Fine-tune the ALREADY-TRAINED CNN checkpoint (pipeline/models/cnn_model.pt)
instead of training it from scratch. Use this after cnn_model.pt already
exists (train.py has been run at least once); use train.py --model cnn if
you actually want to start over from random weights.

Usage:
    python finetune.py
    python finetune.py --epochs 10 --lr 5e-5

Why a separate script instead of a `--resume` flag on train.py: fine-tuning
has a different lifecycle from training-from-scratch. It loads existing
weights instead of random-initializing them, defaults to a much smaller LR
(nudging already-converged weights, not learning from nothing), and --
critically -- must never silently make the committed model worse: it only
overwrites cnn_model.pt if an epoch actually beats the val accuracy already
recorded in metrics.json (see main() below). None of that applies to
train.py's from-scratch runs, so bolting it on as a flag would mean every
reader has to mentally branch on "is --resume set?" through the whole file.

run_one_epoch and plot_training_curves are imported from train.py rather
than duplicated -- the epoch loop and plotting logic don't change just
because the starting weights aren't random.
"""

import argparse
import json

import torch
import torch.nn as nn
import torch.optim as optim

import config
from dataset import get_dataloaders
from evaluate import evaluate_model
from model import SimpleCNN
from train import plot_training_curves, run_one_epoch


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Fine-tune the existing CNN checkpoint.")
    parser.add_argument("--epochs", type=int, default=10)
    # An order of magnitude below train.py's from-scratch default
    # (config.LEARNING_RATE == 1e-3): cnn_model.pt's weights already
    # converged once, so a large LR here would undo that progress before
    # the model has a chance to make small, targeted improvements.
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    torch.manual_seed(config.RANDOM_SEED)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    if not config.MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No existing CNN checkpoint at {config.MODEL_PATH} to fine-tune. "
            "Run `python train.py` first to produce one from scratch."
        )

    train_loader, val_loader, test_loader, class_names = get_dataloaders(batch_size=args.batch_size)

    model = SimpleCNN(num_classes=len(class_names)).to(device)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=device))

    # Record the accuracy we're starting from so fine-tuning can never
    # silently ship a WORSE model than what was already committed: below,
    # cnn_model.pt is only overwritten once an epoch's val accuracy beats
    # this baseline, exactly like train.py's own "keep only the best
    # checkpoint" rule, just seeded from the existing metrics.json instead
    # of -1.0.
    starting_val_accuracy = -1.0
    if config.METRICS_PATH.exists():
        with open(config.METRICS_PATH) as f:
            starting_val_accuracy = json.load(f).get("best_val_accuracy", -1.0)
    print(f"Starting from checkpoint with recorded best_val_accuracy={starting_val_accuracy:.4f}")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_accuracy = starting_val_accuracy
    improved = False

    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = run_one_epoch(model, train_loader, criterion, optimizer, device, train=True)
        val_loss, val_acc = run_one_epoch(model, val_loader, criterion, optimizer, device, train=False)

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        print(f"Epoch {epoch:>2}/{args.epochs} | "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

        if val_acc > best_val_accuracy:
            best_val_accuracy = val_acc
            improved = True
            torch.save(model.state_dict(), config.MODEL_PATH)
            print(f"  -> New best model saved (val_acc={val_acc:.4f}, "
                  f"beats starting {starting_val_accuracy:.4f})")

    if not improved:
        print(f"\nFine-tuning did not beat the starting checkpoint "
              f"(best seen {best_val_accuracy:.4f} vs starting {starting_val_accuracy:.4f}). "
              f"{config.MODEL_PATH} was left untouched.")
        return

    plot_training_curves(history, output_path=config.TRAINING_CURVES_PATHS["cnn"])

    # Reload the best fine-tuned checkpoint (not necessarily the last
    # epoch) before the final, held-out test evaluation.
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=device))
    test_accuracy, report, cm = evaluate_model(
        model, test_loader, class_names, device,
        confusion_matrix_path=config.CONFUSION_MATRIX_PATHS["cnn"],
    )
    print(f"\nFinal test accuracy after fine-tuning: {test_accuracy * 100:.2f}%\n")
    print(report)

    metrics = {
        "best_val_accuracy": best_val_accuracy,
        "test_accuracy": test_accuracy,
        "epochs_trained": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "fine_tuned_from_val_accuracy": starting_val_accuracy,
    }
    with open(config.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved updated model weights to {config.MODEL_PATH}")
    print(f"Saved updated metrics to {config.METRICS_PATH}")


if __name__ == "__main__":
    main()
