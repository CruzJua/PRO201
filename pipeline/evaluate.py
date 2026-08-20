"""
Evaluation utilities: turn a trained model + a DataLoader into human-readable
accuracy numbers, a classification report, and a confusion matrix plot.

`evaluate_model()` is imported by train.py (to score the held-out test set
right after training) AND can be run standalone:

    python evaluate.py

which reloads the saved checkpoint from pipeline/models/ and re-evaluates it
on the Test set -- handy if you just want to re-check accuracy without
retraining from scratch.
"""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix

import config


def evaluate_model(model, data_loader, class_names, device):
    """
    Runs the model over every batch in data_loader and returns:
        - accuracy (float, 0-1)
        - report (str, sklearn's classification_report -- precision/recall/
          f1 per class, which matters a lot for medical data where classes
          are imbalanced and false negatives are costlier than false positives)
        - confusion matrix (np.ndarray)
    """
    model.eval()
    all_predictions = []
    all_labels = []

    with torch.no_grad():
        for images, labels in data_loader:
            images = images.to(device)
            outputs = model(images)
            predictions = outputs.argmax(dim=1).cpu().numpy()
            all_predictions.extend(predictions)
            all_labels.extend(labels.numpy())

    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)

    accuracy = float((all_predictions == all_labels).mean())
    report = classification_report(all_labels, all_predictions, target_names=class_names, digits=4)
    cm = confusion_matrix(all_labels, all_predictions)

    save_confusion_matrix(cm, class_names)

    return accuracy, report, cm


def save_confusion_matrix(cm, class_names):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title("Confusion Matrix (Test Set)")

    # Write the raw count into each cell so the plot is readable without a
    # separate legend/table.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black")

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.CONFUSION_MATRIX_PATH)
    plt.close(fig)


def main():
    """Standalone entry point: reload the saved checkpoint and re-evaluate it."""
    from dataset import get_dataloaders
    from model import SimpleCNN

    if not config.MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No saved model found at {config.MODEL_PATH}. Run `python train.py` first."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(config.CLASS_NAMES_PATH) as f:
        class_names = json.load(f)

    _, _, test_loader, _ = get_dataloaders()

    model = SimpleCNN(num_classes=len(class_names)).to(device)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=device))

    accuracy, report, _ = evaluate_model(model, test_loader, class_names, device)
    print(f"Test accuracy: {accuracy * 100:.2f}%\n")
    print(report)


if __name__ == "__main__":
    main()
