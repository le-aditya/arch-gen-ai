"""Trains a Decision Tree and a Random Forest, picks the better model by F1, serializes it."""
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier

from backend.ml.src.preprocess import build_dataset, FEATURE_COLUMNS

MODELS_DIR = Path(__file__).parent.parent / "models"


def train_models(X_train, y_train):
    tree = DecisionTreeClassifier(
        max_depth=6, min_samples_leaf=5, random_state=42)
    tree.fit(X_train, y_train)

    forest = RandomForestClassifier(
        n_estimators=200, max_depth=10, min_samples_leaf=3, random_state=42
    )
    forest.fit(X_train, y_train)

    return {"decision_tree": tree, "random_forest": forest}


def select_best(models, X_test, y_test):
    best_name, best_model, best_f1 = None, None, -1
    for name, model in models.items():
        preds = model.predict(X_test)
        f1 = f1_score(y_test, preds, average="macro")
        print(f"{name}: macro F1 = {f1:.4f}")
        if f1 > best_f1:
            best_name, best_model, best_f1 = name, model, f1
    return best_name, best_model, best_f1


def main():
    X_train, X_test, y_train, y_test, encoders = build_dataset()
    models = train_models(X_train, y_train)
    best_name, best_model, best_f1 = select_best(models, X_test, y_test)
    print(f"\nSelected model: {best_name} (macro F1 = {best_f1:.4f})")

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(best_model, MODELS_DIR / "architecture_classifier.joblib")
    joblib.dump(encoders, MODELS_DIR / "encoders.joblib")
    joblib.dump(FEATURE_COLUMNS, MODELS_DIR / "feature_columns.joblib")
    joblib.dump(best_name, MODELS_DIR / "selected_model.joblib")
    print(f"Serialized {best_name} to {MODELS_DIR}")


if __name__ == "__main__":
    main()
