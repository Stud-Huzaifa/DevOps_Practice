from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    mean_absolute_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from gamescope_ai.features import collect_input_features, prepare_training_data


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "steam_top_games_2026.csv"
ARTIFACT_DIR = ROOT / "artifacts"


def build_preprocessor():
    numeric_cols = [
        "price_usd",
        "metacritic_score",
        "required_age",
        "dlc_count",
        "achievements",
        "recommendations",
        "avg_playtime_forever",
        "peak_ccu",
        "positive_reviews",
        "negative_reviews",
        "game_age",
        "review_ratio",
        "platform_coverage",
        "genre_count",
        "tag_count",
        "category_count",
        "playtime_signal",
        "peak_ccu_signal",
        "recommendation_signal",
    ]
    bool_cols = ["is_free", "platforms_win", "platforms_mac", "platforms_linux", "coming_soon"]
    cat_cols = ["developer", "publisher"]

    numeric_pipeline = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    bool_pipeline = Pipeline(steps=[("imputer", SimpleImputer(strategy="most_frequent"))])
    cat_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=20)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("bool", bool_pipeline, bool_cols),
            ("cat", cat_pipeline, cat_cols),
            ("genres_tfidf", TfidfVectorizer(max_features=300), "genres"),
            ("tags_tfidf", TfidfVectorizer(max_features=700), "tags"),
            ("categories_tfidf", TfidfVectorizer(max_features=200), "categories"),
            ("description_tfidf", TfidfVectorizer(max_features=600, stop_words="english"), "short_description"),
        ],
        remainder="drop",
    )


def main():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(DATA_PATH)
    engineered, y_class, y_profit = prepare_training_data(raw)
    features, vocab = collect_input_features(engineered)

    X_train, X_test, y_train, y_test, p_train, p_test = train_test_split(
        features, y_class, y_profit, test_size=0.2, random_state=42, stratify=y_class
    )

    classifier_candidates = {
        "random_forest": RandomForestClassifier(
            n_estimators=450,
            max_depth=20,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=700,
            max_depth=None,
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }
    regressor_candidates = {
        "random_forest": RandomForestRegressor(
            n_estimators=500, max_depth=20, min_samples_leaf=2, random_state=42, n_jobs=-1
        ),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=700, max_depth=None, min_samples_leaf=1, random_state=42, n_jobs=-1
        ),
    }

    best_clf_name, best_clf_score, class_pipeline, class_pred = None, -1.0, None, None
    for name, clf in classifier_candidates.items():
        candidate = Pipeline([("preprocessor", build_preprocessor()), ("model", clf)])
        candidate.fit(X_train, y_train)
        pred = candidate.predict(X_test)
        score = balanced_accuracy_score(y_test, pred)
        if score > best_clf_score:
            best_clf_name, best_clf_score, class_pipeline, class_pred = name, score, candidate, pred

    best_reg_name, best_reg_score, profit_pipeline, profit_pred = None, -np.inf, None, None
    for name, reg in regressor_candidates.items():
        candidate = Pipeline([("preprocessor", build_preprocessor()), ("model", reg)])
        candidate.fit(X_train, p_train)
        pred = candidate.predict(X_test)
        score = r2_score(p_test, pred)
        if score > best_reg_score:
            best_reg_name, best_reg_score, profit_pipeline, profit_pred = name, score, candidate, pred

    metrics = {
        "selected_classifier": best_clf_name,
        "selected_regressor": best_reg_name,
        "classification_accuracy": float(accuracy_score(y_test, class_pred)),
        "classification_balanced_accuracy": float(balanced_accuracy_score(y_test, class_pred)),
        "classification_macro_f1": float(f1_score(y_test, class_pred, average="macro")),
        "classification_report": classification_report(y_test, class_pred, output_dict=True),
        "profit_mae_log": float(mean_absolute_error(p_test, profit_pred)),
        "profit_r2_log": float(r2_score(p_test, profit_pred)),
    }

    joblib.dump(class_pipeline, ARTIFACT_DIR / "success_classifier.joblib")
    joblib.dump(profit_pipeline, ARTIFACT_DIR / "profit_regressor.joblib")

    metadata = {
        "metrics": metrics,
        "training_rows": int(len(features)),
        "top_genres": vocab["genres"][:50],
        "top_tags": vocab["tags"][:100],
        "median_price": float(np.nanmedian(engineered["price_usd"])),
        "high_success_price_band": [
            float(engineered.loc[engineered["success_label"] == "High Success", "price_usd"].quantile(0.25)),
            float(engineered.loc[engineered["success_label"] == "High Success", "price_usd"].quantile(0.75)),
        ],
    }
    (ARTIFACT_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
