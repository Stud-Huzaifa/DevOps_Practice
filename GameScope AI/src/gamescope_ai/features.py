from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


CURRENT_YEAR = datetime.now().year


def safe_divide(numerator: pd.Series, denominator: pd.Series, default: float = 0.0) -> pd.Series:
    den = denominator.replace(0, np.nan)
    result = numerator / den
    return result.fillna(default)


def parse_owner_range(value: str | float | int) -> float:
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", "").strip()
    if ".." in cleaned:
        left, right = cleaned.split("..")
        try:
            return (float(left.strip()) + float(right.strip())) / 2.0
        except ValueError:
            return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def split_tokens(value: str) -> List[str]:
    if pd.isna(value):
        return []
    return [token.strip().lower() for token in str(value).split(",") if token.strip()]


def release_to_age(release_date: str | float) -> float:
    if pd.isna(release_date):
        return 0.0
    parsed = pd.to_datetime(release_date, errors="coerce")
    if pd.isna(parsed):
        return 0.0
    return max(0.0, CURRENT_YEAR - parsed.year)


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    output = df.copy()

    output["owners_mid"] = output["estimated_owners"].map(parse_owner_range)
    output["review_total"] = output["positive_reviews"].fillna(0) + output["negative_reviews"].fillna(0)
    output["review_ratio"] = safe_divide(output["positive_reviews"].fillna(0), output["review_total"], default=0.5)
    output["game_age"] = output["release_date"].map(release_to_age)
    output["estimated_revenue"] = output["owners_mid"] * output["price_usd"].fillna(0)
    output["platform_coverage"] = (
        output["platforms_win"].fillna(False).astype(int)
        + output["platforms_mac"].fillna(False).astype(int)
        + output["platforms_linux"].fillna(False).astype(int)
    )
    output["genre_count"] = output["genres"].map(lambda v: len(split_tokens(v)))
    output["tag_count"] = output["tags"].map(lambda v: len(split_tokens(v)))
    output["category_count"] = output["categories"].map(lambda v: len(split_tokens(v)))
    output["playtime_signal"] = np.log1p(output["avg_playtime_forever"].fillna(0))
    output["peak_ccu_signal"] = np.log1p(output["peak_ccu"].fillna(0))
    output["recommendation_signal"] = np.log1p(output["recommendations"].fillna(0))

    return output


def construct_success_score(df: pd.DataFrame) -> pd.Series:
    normalized = pd.DataFrame(index=df.index)
    normalized["owners"] = np.log1p(df["owners_mid"]) / np.log1p(max(df["owners_mid"].max(), 1.0))
    normalized["review_ratio"] = df["review_ratio"].clip(0, 1)
    normalized["engagement"] = np.log1p(df["avg_playtime_forever"].fillna(0)) / np.log1p(
        max(df["avg_playtime_forever"].max(), 1.0)
    )
    normalized["ccu"] = np.log1p(df["peak_ccu"].fillna(0)) / np.log1p(max(df["peak_ccu"].max(), 1.0))
    normalized["revenue"] = np.log1p(df["estimated_revenue"]) / np.log1p(max(df["estimated_revenue"].max(), 1.0))

    score = (
        0.30 * normalized["owners"]
        + 0.20 * normalized["review_ratio"]
        + 0.20 * normalized["engagement"]
        + 0.15 * normalized["ccu"]
        + 0.15 * normalized["revenue"]
    ) * 100.0
    return score


def categorize_success(score: pd.Series) -> pd.Series:
    q1, q2 = score.quantile([0.33, 0.66]).tolist()
    bins = [-np.inf, q1, q2, np.inf]
    labels = ["Low Success", "Medium Success", "High Success"]
    return pd.cut(score, bins=bins, labels=labels)


@dataclass
class ArtifactBundle:
    classifier_path: str
    regressor_path: str
    metadata_path: str


def prepare_training_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    engineered = build_feature_frame(df)
    engineered["success_score"] = construct_success_score(engineered)
    engineered["success_label"] = categorize_success(engineered["success_score"])
    engineered["profit_target"] = np.log1p(engineered["estimated_revenue"].clip(lower=0))
    cleaned = engineered.dropna(subset=["success_label"])
    return cleaned, cleaned["success_label"], cleaned["profit_target"]


def collect_input_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
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
    text_cols = ["genres", "categories", "tags", "short_description", "developer", "publisher"]

    feature_df = df[numeric_cols + bool_cols + text_cols].copy()
    for col in bool_cols:
        feature_df[col] = feature_df[col].fillna(False).astype(int)
    for col in text_cols:
        feature_df[col] = feature_df[col].fillna("").astype(str)
    text_vocab = {
        "genres": sorted({token for text in df["genres"].fillna("") for token in split_tokens(text)}),
        "tags": sorted({token for text in df["tags"].fillna("") for token in split_tokens(text)}),
    }
    return feature_df, text_vocab
