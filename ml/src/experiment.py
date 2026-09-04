"""Four-way experiment (PRD sections 17-18): Threshold vs LLM-only vs ML vs LLM+ML,
evaluated on the same held-out set -- the real case studies (PRD section 11.1),
since those have both descriptive text and ground-truth labels."""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from baseline import predict_baseline  # noqa: E402
from llm_only import predict_llm_only  # noqa: E402
from preprocess import ORDINAL_MAP  # noqa: E402

from app.services.feature_service import extract_features  # noqa: E402
from app.services.llm_service import get_provider  # noqa: E402
from app.schemas.schemas import ProjectInput  # noqa: E402

DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"


def load_case_studies():
    df = pd.read_csv(DATA_DIR / "real_case_studies.csv")
    df["real_time"] = df["real_time"].astype(bool)
    df["payment"] = df["payment"].astype(bool)
    return df


def build_description(row) -> str:
    return str(row["case_name"])


def ml_predict_from_row(row, model, encoders, feature_columns):
    vec = {
        "team_size": float(row["team_size"]),
        "budget": float(ORDINAL_MAP[row["budget"]]),
        "expected_users": float(ORDINAL_MAP[row["expected_users"]]),
        "number_of_roles": float(row["number_of_roles"]),
        "number_of_modules": float(row["number_of_modules"]),
        "real_time": float(row["real_time"]),
        "payment": float(row["payment"]),
        "external_integrations": float(row["external_integrations"]),
        "data_complexity": float(ORDINAL_MAP[row["data_complexity"]]),
        "availability": float(ORDINAL_MAP[row["availability"]]),
    }
    known = set(encoders.domain_classes_)
    domain = row["domain"] if row["domain"] in known else encoders.domain_classes_[0]
    vec["domain"] = float(encoders.domain_encoder.transform([domain])[0])
    X = pd.DataFrame([vec])[feature_columns]
    pred = model.predict(X)[0]
    return encoders.label_encoder.inverse_transform([pred])[0]


def llm_plus_ml_predict(row, model, encoders, feature_columns, provider):
    description = build_description(row)
    requirements = provider.extract_requirements(description)
    project_input = ProjectInput(
        description=description,
        team_size=int(row["team_size"]),
        budget=row["budget"],
        expected_users=row["expected_users"],
        availability=row["availability"],
    )
    features = extract_features(project_input, requirements)

    vec = {
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
    known = set(encoders.domain_classes_)
    domain = features.domain if features.domain in known else encoders.domain_classes_[0]
    vec["domain"] = float(encoders.domain_encoder.transform([domain])[0])
    X = pd.DataFrame([vec])[feature_columns]
    pred = model.predict(X)[0]
    return encoders.label_encoder.inverse_transform([pred])[0]


def metrics(y_true, y_pred, labels):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "recall": recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "f1": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
    }


def main():
    df = load_case_studies()
    model = joblib.load(MODELS_DIR / "architecture_classifier.joblib")
    encoders = joblib.load(MODELS_DIR / "encoders.joblib")
    feature_columns = joblib.load(MODELS_DIR / "feature_columns.joblib")
    provider = get_provider()

    y_true = df["architecture"].tolist()
    labels = sorted(set(y_true))

    preds = {"threshold": [], "llm_only": [], "ml": [], "llm_plus_ml": []}

    for _, row in df.iterrows():
        preds["threshold"].append(predict_baseline(row))
        preds["llm_only"].append(predict_llm_only(build_description(row)))
        preds["ml"].append(ml_predict_from_row(row, model, encoders, feature_columns))
        preds["llm_plus_ml"].append(llm_plus_ml_predict(row, model, encoders, feature_columns, provider))

    results = {name: metrics(y_true, p, labels) for name, p in preds.items()}

    print(f"Held-out set: {len(df)} real case studies\n")
    print(f"{'Metric':<12}{'Threshold':>12}{'LLM-only':>12}{'ML':>12}{'LLM+ML':>12}")
    for metric_name in ("accuracy", "precision", "recall", "f1"):
        row_vals = [results[k][metric_name] for k in ("threshold", "llm_only", "ml", "llm_plus_ml")]
        print(f"{metric_name:<12}" + "".join(f"{v:>12.3f}" for v in row_vals))

    out_path = DATA_DIR.parent / "experiment_results.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved detailed results to {out_path}")
    return results


if __name__ == "__main__":
    main()
