"""Cleaning, encoding, and train/test splitting for the architecture dataset."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATA_DIR = Path(__file__).parent.parent / "data"

ORDINAL_MAP = {"low": 0, "medium": 1, "high": 2}

FEATURE_COLUMNS = [
    "team_size",
    "budget",
    "expected_users",
    "number_of_roles",
    "number_of_modules",
    "real_time",
    "payment",
    "external_integrations",
    "data_complexity",
    "availability",
    "domain",
]

LABEL_COLUMN = "architecture"


def load_synthetic_dataset():
    path = DATA_DIR / "synthetic_dataset.csv"
    df = pd.read_csv(path)
    return clean(df)


def clean(df):
    df = df.dropna(subset=FEATURE_COLUMNS + [LABEL_COLUMN]).copy()
    df = df.drop_duplicates()
    valid_labels = {"Monolith", "Microservices", "Serverless"}
    df = df[df[LABEL_COLUMN].isin(valid_labels)]
    # Guard against impossible combinations (e.g. negative counts).
    df = df[(df["team_size"] > 0) & (df["number_of_modules"] > 0) & (df["number_of_roles"] > 0)]
    df = df[df["external_integrations"] >= 0]
    return df.reset_index(drop=True)


class Encoders:
    """Holds fitted encoders so the backend can reuse them at inference time."""

    def __init__(self):
        self.domain_encoder = LabelEncoder()
        self.label_encoder = LabelEncoder()
        self.domain_classes_ = None

    def fit(self, df):
        self.domain_encoder.fit(df["domain"])
        self.domain_classes_ = list(self.domain_encoder.classes_)
        self.label_encoder.fit(df[LABEL_COLUMN])
        return self

    def transform_features(self, df):
        out = pd.DataFrame(index=df.index)
        out["team_size"] = df["team_size"].astype(float)
        out["budget"] = df["budget"].map(ORDINAL_MAP).astype(float)
        out["expected_users"] = df["expected_users"].map(ORDINAL_MAP).astype(float)
        out["number_of_roles"] = df["number_of_roles"].astype(float)
        out["number_of_modules"] = df["number_of_modules"].astype(float)
        out["real_time"] = df["real_time"].astype(bool).astype(float)
        out["payment"] = df["payment"].astype(bool).astype(float)
        out["external_integrations"] = df["external_integrations"].astype(float)
        out["data_complexity"] = df["data_complexity"].map(ORDINAL_MAP).astype(float)
        out["availability"] = df["availability"].map(ORDINAL_MAP).astype(float)

        # Unseen domains at inference time fall back to a neutral encoding.
        known = set(self.domain_classes_)
        domain_vals = df["domain"].where(df["domain"].isin(known), self.domain_classes_[0])
        out["domain"] = self.domain_encoder.transform(domain_vals).astype(float)
        return out

    def transform_labels(self, df):
        return self.label_encoder.transform(df[LABEL_COLUMN])

    def inverse_label(self, encoded):
        return self.label_encoder.inverse_transform(np.atleast_1d(encoded))


def split(df, encoders, test_size=0.2, seed=42):
    X = encoders.transform_features(df)
    y = encoders.transform_labels(df)
    return train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)


def build_dataset(test_size=0.2, seed=42):
    df = load_synthetic_dataset()
    encoders = Encoders().fit(df)
    X_train, X_test, y_train, y_test = split(df, encoders, test_size=test_size, seed=seed)
    return X_train, X_test, y_train, y_test, encoders
