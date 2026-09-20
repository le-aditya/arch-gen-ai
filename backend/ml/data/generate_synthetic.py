"""Generates a synthetic training dataset for the architecture classifier.

Deliberately avoids simple threshold rules (e.g. `if users > X: microservices`).
Instead each row is scored via multiple interacting, weighted features plus
Gaussian noise, then the label is sampled from the resulting score distribution
so classes overlap near decision boundaries -- forcing the model to learn
combinations rather than a single cutoff, per PRD section 12.
"""
import csv
import random
from pathlib import Path

random.seed(42)

BUDGETS = ["low", "medium", "high"]
USER_SCALES = ["low", "medium", "high"]
DATA_COMPLEXITY = ["low", "medium", "high"]
AVAILABILITY = ["low", "medium", "high"]
DOMAINS = [
    "food_delivery", "e_commerce", "social_media", "fintech", "healthtech",
    "edtech", "logistics", "gaming", "media_streaming", "productivity_tool",
    "iot_platform", "booking_platform", "marketplace", "analytics_dashboard",
    "content_management",
]

ORDINAL = {"low": 0, "medium": 1, "high": 2}

ARCHITECTURES = ["Monolith", "Microservices", "Serverless"]


def sample_row(rng):
    team_size = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 15, 20])
    budget = rng.choice(BUDGETS)
    expected_users = rng.choice(USER_SCALES)
    number_of_roles = rng.randint(1, 6)
    number_of_modules = rng.randint(2, 12)
    real_time = rng.random() < 0.35
    payment = rng.random() < 0.45
    external_integrations = rng.randint(0, 6)
    data_complexity = rng.choice(DATA_COMPLEXITY)
    availability = rng.choice(AVAILABILITY)
    domain = rng.choice(DOMAINS)

    return {
        "team_size": team_size,
        "budget": budget,
        "expected_users": expected_users,
        "number_of_roles": number_of_roles,
        "number_of_modules": number_of_modules,
        "real_time": real_time,
        "payment": payment,
        "external_integrations": external_integrations,
        "data_complexity": data_complexity,
        "availability": availability,
        "domain": domain,
    }


def score_row(row, rng):
    """Returns (microservices_score, serverless_score, monolith_score) with noise."""
    scale = ORDINAL[row["expected_users"]]
    avail = ORDINAL[row["availability"]]
    complexity = ORDINAL[row["data_complexity"]]
    budget = ORDINAL[row["budget"]]

    # Interacting, weighted contributions -- not a single cutoff.
    micro = (
        0.9 * scale
        + 0.8 * avail
        + 0.6 * (row["number_of_modules"] / 12)
        + 0.5 * (row["external_integrations"] / 6)
        + 0.4 * complexity
        + 0.3 * min(row["team_size"] / 10, 1.5)
        - 0.5 * (2 - budget)
    )

    serverless = (
        1.3 * (1 - min(row["team_size"] / 8, 1))
        + 1.1 * (2 - budget)
        + 0.9 * (1 if row["number_of_modules"] <= 6 else 0.1)
        + 0.4 * row["external_integrations"] / 6
        + 0.3 * (1 if row["real_time"] else 0)
        - 0.6 * complexity
        - 0.5 * avail
        + (0.8 if scale == 0 else 0)
    )

    monolith = (
        0.8 * (2 - scale)
        + 0.6 * (2 - avail)
        + 0.5 * (1 if row["number_of_modules"] <= 5 else 0)
        + 0.4 * (1 if row["team_size"] <= 4 else 0)
        + 0.3 * (2 - complexity)
        - 0.3 * (row["external_integrations"] / 6)
    )

    # Payment/real-time nudge microservices/serverless slightly -- not deterministically.
    if row["payment"]:
        micro += 0.2
        serverless += 0.1
    if row["real_time"]:
        micro += 0.3

    noise = lambda: rng.gauss(0, 0.4)
    return micro + noise(), serverless + noise(), monolith + noise()


def label_row(row, rng):
    micro, serverless, monolith = score_row(row, rng)
    scores = {"Microservices": micro, "Serverless": serverless, "Monolith": monolith}
    # Softmax-ish sampling instead of pure argmax, to keep boundaries fuzzy.
    total = sum(2.71828 ** (v * 0.8) for v in scores.values())
    probs = {k: (2.71828 ** (v * 0.8)) / total for k, v in scores.items()}
    r = rng.random()
    cumulative = 0.0
    for label, p in probs.items():
        cumulative += p
        if r <= cumulative:
            return label
    return max(scores, key=scores.get)


def generate(n_rows=900, seed=42):
    rng = random.Random(seed)
    rows = []
    for _ in range(n_rows):
        row = sample_row(rng)
        row["architecture"] = label_row(row, rng)
        rows.append(row)
    return rows


def main():
    rows = generate()
    out_path = Path(__file__).parent / "synthetic_dataset.csv"
    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    counts = {}
    for row in rows:
        counts[row["architecture"]] = counts.get(row["architecture"], 0) + 1
    print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"Class distribution: {counts}")


if __name__ == "__main__":
    main()
