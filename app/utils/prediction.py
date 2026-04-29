import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression


def build_features(p1, p2):
    return [
        (p1["points"] - p2["points"]) / 1000,
        (p2["rank_position"] - p1["rank_position"]) / 100,
        (p1["movement"] - p2["movement"]) / 10,
        (p1["competitions_played"] - p2["competitions_played"]) / 50
    ]


def train_model(df):
    data = []

    players = df.to_dict("records")

    for i in range(len(players)):
        for j in range(i + 1, len(players)):

            p1 = players[i]
            p2 = players[j]

            features = build_features(p1, p2)

            # label: 1 if p1 stronger
            prob = 1 / (1 + np.exp(-(p1["points"] - p2["points"]) / 800))

            label = 1 if np.random.rand() < prob else 0

            data.append(features + [label])
            data.append([-f for f in features] + [1 - label])

    cols = [
        "points_diff",
        "rank_diff",
        "movement_diff",
        "matches_diff",
        "label"
    ]

    train_df = pd.DataFrame(data, columns=cols)

    X = train_df.drop("label", axis=1)
    y = train_df["label"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    return model


def predict(model, p1, p2):
    features = build_features(p1, p2)
    prob = model.predict_proba([features])[0][1]

    # smoothing (keep realistic)
    prob = max(0.05, min(0.95, prob))

    return prob, 1 - prob