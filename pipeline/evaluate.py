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


def evaluate_model(model, data_loader, class_names, device, confusion_matrix_path=config.CONFUSION_MATRIX_PATH):
    """
    Runs the model over every batch in data_loader and returns:
        - accuracy (float, 0-1)
        - report (str, sklearn's classification_report -- precision/recall/
          f1 per class, which matters a lot for medical data where classes
          are imbalanced and false negatives are costlier than false positives)
        - confusion matrix (np.ndarray)

    confusion_matrix_path is a parameter (not just config.CONFUSION_MATRIX_PATH
    baked in) so train.py/finetune.py can point it at the right file for
    whichever of the three architectures they're currently evaluating --
    otherwise a CNN run and a ViT run would overwrite the same plot.
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

    save_confusion_matrix(cm, class_names, output_path=confusion_matrix_path)

    return accuracy, report, cm


def save_confusion_matrix(cm, class_names, output_path=config.CONFUSION_MATRIX_PATH):
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
    fig.savefig(output_path)
    plt.close(fig)


def main():
    """Standalone entry point: reload a saved checkpoint and re-evaluate it.

    Usage:
        python evaluate.py                  # re-checks the CNN (default)
        python evaluate.py --model vit
        python evaluate.py --model convnext
    """
    import argparse

    from dataset import get_dataloaders
    from model import MODEL_BUILDERS

    parser = argparse.ArgumentParser(description="Re-evaluate a saved checkpoint on the test set.")
    parser.add_argument("--model", choices=config.MODEL_NAMES, default="cnn")
    args = parser.parse_args()

    model_path = config.MODEL_PATHS[args.model]
    if not model_path.exists():
        raise FileNotFoundError(
            f"No saved model found at {model_path}. Run `python train.py --model {args.model}` first."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(config.CLASS_NAMES_PATH) as f:
        class_names = json.load(f)

    _, _, test_loader, _ = get_dataloaders(image_size=config.IMAGE_SIZES[args.model])

    model = MODEL_BUILDERS[args.model](num_classes=len(class_names), pretrained=False).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))

    accuracy, report, _ = evaluate_model(
        model, test_loader, class_names, device,
        confusion_matrix_path=config.CONFUSION_MATRIX_PATHS[args.model],
    )
    print(f"Test accuracy ({args.model}): {accuracy * 100:.2f}%\n")
    print(report)


if __name__ == "__main__":
    main()
