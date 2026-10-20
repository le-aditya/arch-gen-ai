"""Performance metrics for the serialized architecture classifier.

Reports the model's scores on the stratified held-out split of the synthetic
dataset (accuracy, macro precision/recall/F1, per-class report, confusion
matrix), plus a sanity check on the 35 hand-labelled real-world case studies.
Metrics are written to backend/ml/model_metrics.json.
"""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

# Must match the import name train.py used when pickling the encoders.
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from preprocess import build_dataset  # noqa: E402

ML_ROOT = Path(__file__).parent.parent
MODELS_DIR = ML_ROOT / "models"
DATA_DIR = ML_ROOT / "data"


def load_artifacts():
    model = joblib.load(MODELS_DIR / "architecture_classifier.joblib")
    encoders = joblib.load(MODELS_DIR / "encoders.joblib")
    return model, encoders


def score(y_true, y_pred, labels):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(
            y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "recall": float(recall_score(
            y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "f1": float(f1_score(
            y_true, y_pred, labels=labels, average="macro", zero_division=0)),
    }


def evaluate_holdout(model, encoders):
    """Scores the model on the same held-out split it was trained against."""
    X_train, X_test, y_train, y_test, _ = build_dataset()
    labels = list(encoders.label_encoder.classes_)
    preds = model.predict(X_test)

    results = score(y_test, preds, labels=list(range(len(labels))))
    results.update({
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "labels": labels,
        "confusion_matrix": confusion_matrix(
            y_test, preds, labels=list(range(len(labels)))).tolist(),
    })
    return results, y_test, preds, labels


def load_real_case_studies():
    df = pd.read_csv(DATA_DIR / "real_case_studies.csv")
    for column in ("real_time", "payment"):
        df[column] = df[column].astype(bool)
    return df


def evaluate_real_case_studies(model, encoders):
    """Agreement with the hand-labelled case studies -- these are NOT in training.

    A sanity check that the model generalises beyond the synthetic distribution.
    """
    df = load_real_case_studies()
    X = encoders.transform_features(df)
    preds = encoders.inverse_label(model.predict(X))
    labels = list(encoders.label_encoder.classes_)
    results = score(df["architecture"], preds, labels=labels)
    results["n"] = int(len(df))
    results["per_class_recall"] = {
        label: float((preds[df["architecture"].to_numpy() == label] == label).mean())
        for label in labels
    }
    return results


def main():
    model, encoders = load_artifacts()

    holdout, y_test, preds, labels = evaluate_holdout(model, encoders)
    real = evaluate_real_case_studies(model, encoders)

    print(f"Held-out set: {holdout['n_test']} rows "
          f"({holdout['n_train']} for training)\n")
    for metric_name in ("accuracy", "precision", "recall", "f1"):
        print(f"{metric_name.capitalize():<12}{holdout[metric_name]:>8.4f}")
    print(f"\nLabels: {labels}")
    print("Confusion matrix (rows = actual, cols = predicted):")
    print(pd.DataFrame(holdout["confusion_matrix"], index=labels, columns=labels))
    print()
    print(classification_report(
        y_test, preds, labels=list(range(len(labels))),
        target_names=labels, zero_division=0))

    print(f"Real case-study check ({real['n']} hand-labelled cases, "
          "not used in training):")
    print(f"  accuracy {real['accuracy']:.4f}  macro F1 {real['f1']:.4f}")
    for label, value in real["per_class_recall"].items():
        print(f"  recall {label:<14}{value:.4f}")

    out_path = ML_ROOT / "model_metrics.json"
    out_path.write_text(json.dumps({
        "model": "random_forest_v2",
        "trained_on": "synthetic_dataset.csv",
        "holdout": holdout,
        "real_case_studies": real,
    }, indent=2))
    print(f"\nSaved metrics to {out_path}")
    return holdout


if __name__ == "__main__":
    main()
