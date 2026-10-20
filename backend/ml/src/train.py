"""Trains the architecture classifier and serializes it for the backend.

The deployed model is a single Random Forest: it predicts the architecture
style (Monolith / Microservices / Serverless) and exposes both class
probabilities and feature importances, which the API surfaces to the UI.
Scored on the stratified held-out set by `evaluate.py`.
"""
import sys
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier

# Import `preprocess` as a top-level module: the Encoders instance is pickled
# into encoders.joblib, and the backend unpickles it by adding this directory
# to sys.path. Importing it as `backend.ml.src.preprocess` would make the
# artifact unloadable whenever the repo root is not importable (e.g. Render).
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from preprocess import FEATURE_COLUMNS, build_dataset  # noqa: E402

MODELS_DIR = Path(__file__).parent.parent / "models"

MODEL_NAME = "random_forest_v2"

MODEL_PARAMS = {
    "n_estimators": 300,
    "max_depth": 12,
    "min_samples_leaf": 2,
    "class_weight": "balanced",
    "random_state": 42,
    "n_jobs": -1,
}


def build_model() -> RandomForestClassifier:
    return RandomForestClassifier(**MODEL_PARAMS)


def main():
    X_train, X_test, y_train, y_test, encoders = build_dataset()

    model = build_model()
    model.fit(X_train, y_train)

    print(f"Trained {MODEL_NAME} on {len(X_train)} rows "
          f"({X_train.shape[1]} features), {len(X_test)} held out")
    print(f"Held-out accuracy: {model.score(X_test, y_test):.4f}")

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODELS_DIR / "architecture_classifier.joblib")
    joblib.dump(encoders, MODELS_DIR / "encoders.joblib")
    joblib.dump(FEATURE_COLUMNS, MODELS_DIR / "feature_columns.joblib")
    print(f"Serialized model + encoders to {MODELS_DIR}")


if __name__ == "__main__":
    main()
