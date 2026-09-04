"""Prints accuracy/precision/recall/F1/confusion matrix for the serialized model."""
from pathlib import Path

import joblib
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

from preprocess import build_dataset

MODELS_DIR = Path(__file__).parent.parent / "models"


def main():
    X_train, X_test, y_train, y_test, encoders = build_dataset()
    model = joblib.load(MODELS_DIR / "architecture_classifier.joblib")
    selected_name = joblib.load(MODELS_DIR / "selected_model.joblib")

    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, average="macro", zero_division=0)
    rec = recall_score(y_test, preds, average="macro", zero_division=0)
    f1 = f1_score(y_test, preds, average="macro", zero_division=0)
    cm = confusion_matrix(y_test, preds)
    labels = encoders.label_encoder.classes_

    print(f"Model: {selected_name}\n")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1:        {f1:.4f}\n")
    print(f"Labels: {list(labels)}")
    print("Confusion matrix:")
    print(cm)
    print()
    print(classification_report(y_test, preds, target_names=labels, zero_division=0))

    return {
        "model": selected_name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "confusion_matrix": cm.tolist(),
        "labels": list(labels),
    }


if __name__ == "__main__":
    main()
