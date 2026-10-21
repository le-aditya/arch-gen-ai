"""Loads the serialized architecture classifier once at startup and predicts."""
import sys
from pathlib import Path

import joblib
import pandas as pd

from app.schemas.schemas import ClassProbability, FeatureVector, Prediction, TopFactor

ML_ROOT = Path(__file__).parent.parent.parent / "ml"
MODELS_DIR = ML_ROOT / "models"

# The serialized Encoders instance was pickled from ml/src/preprocess.py -- joblib
# needs that module importable by the same name to unpickle it.
_ML_SRC = str(ML_ROOT / "src")
if _ML_SRC not in sys.path:
    sys.path.insert(0, _ML_SRC)

ORDINAL_MAP = {"low": 0, "medium": 1, "high": 2}

FEATURE_LABELS = {
    "team_size": "Team size",
    "budget": "Budget",
    "expected_users": "Expected user scale",
    "number_of_roles": "Number of actor roles",
    "number_of_modules": "Number of modules",
    "real_time": "Real-time requirement",
    "payment": "Payment processing",
    "external_integrations": "External integrations",
    "data_complexity": "Data complexity",
    "availability": "Availability requirement",
    "domain": "Application domain",
}


def _feature_importances(model):
    """Feature importances whether the estimator is bare or inside a pipeline."""
    importances = getattr(model, "feature_importances_", None)
    if importances is not None:
        return importances
    for step in getattr(model, "named_steps", {}).values():
        importances = getattr(step, "feature_importances_", None)
        if importances is not None:
            return importances
    return None


class MLService:
    def __init__(self):
        self.model = joblib.load(MODELS_DIR / "architecture_classifier.joblib")
        self.encoders = joblib.load(MODELS_DIR / "encoders.joblib")
        self.feature_columns = joblib.load(
            MODELS_DIR / "feature_columns.joblib")

    def _vectorize(self, features: FeatureVector) -> pd.DataFrame:
        row = {
            "team_size": float(features.team_size),
            "budget": float(ORDINAL_MAP[features.budget]),
            "expected_users": float(ORDINAL_MAP[features.expected_users]),
            "number_of_roles": float(features.number_of_roles),
            "number_of_modules": float(features.number_of_modules),
            "real_time": float(features.real_time),
            "payment": float(features.payment),
            "external_integrations": float(features.external_integrations),
            "data_complexity": float(ORDINAL_MAP[features.data_complexity]),
            "availability": float(ORDINAL_MAP[features.availability]),
        }
        known_domains = set(self.encoders.domain_classes_)
        domain = features.domain if features.domain in known_domains else self.encoders.domain_classes_[
            0]
        row["domain"] = float(
            self.encoders.domain_encoder.transform([domain])[0])
        return pd.DataFrame([row])[self.feature_columns]

    def predict(self, features: FeatureVector) -> Prediction:
        X = self._vectorize(features)
        proba = self.model.predict_proba(X)[0]
        classes = self.encoders.label_encoder.inverse_transform(
            range(len(proba)))
        best_idx = proba.argmax()
        architecture = classes[best_idx]
        confidence = float(proba[best_idx])

        importances = _feature_importances(self.model)
        top_factors = []
        if importances is not None:
            # Share of the model's TOTAL importance, so each weight is meaningful
            # on its own and the reported factors never add up to 100%.
            total = float(sum(importances)) or 1.0
            ranked = sorted(
                zip(self.feature_columns, importances), key=lambda x: x[1], reverse=True
            )[:5]
            top_factors = [
                TopFactor(name=FEATURE_LABELS.get(name, name),
                          importance=float(v / total))
                for name, v in ranked
            ]

        alternatives = sorted(
            (
                ClassProbability(architecture=str(cls), probability=float(p))
                for cls, p in zip(classes, proba)
            ),
            key=lambda c: c.probability,
            reverse=True,
        )

        return Prediction(
            architecture=architecture,
            confidence=confidence,
            top_factors=top_factors,
            alternatives=alternatives,
        )


_ml_service_instance: MLService | None = None


def get_ml_service() -> MLService:
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLService()
    return _ml_service_instance
