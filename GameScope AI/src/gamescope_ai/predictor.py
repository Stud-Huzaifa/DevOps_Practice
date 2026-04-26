from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd

from gamescope_ai.features import build_feature_frame


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts"


class GameScopePredictor:
    def __init__(self):
        self.classifier = joblib.load(ARTIFACT_DIR / "success_classifier.joblib")
        self.regressor = joblib.load(ARTIFACT_DIR / "profit_regressor.joblib")
        self.metadata = json.loads((ARTIFACT_DIR / "metadata.json").read_text(encoding="utf-8"))

    def _to_frame(self, payload: Dict[str, Any]) -> pd.DataFrame:
        base = pd.DataFrame([payload])
        engineered = build_feature_frame(base)
        required_cols = [
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
            "is_free",
            "platforms_win",
            "platforms_mac",
            "platforms_linux",
            "coming_soon",
            "developer",
            "publisher",
            "genres",
            "categories",
            "tags",
            "short_description",
        ]
        frame = engineered[required_cols].copy()
        for col in ["is_free", "platforms_win", "platforms_mac", "platforms_linux", "coming_soon"]:
            frame[col] = frame[col].fillna(False).astype(int)
        for col in ["genres", "categories", "tags", "short_description", "developer", "publisher"]:
            frame[col] = frame[col].fillna("").astype(str)
        return frame

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        X = self._to_frame(payload)
        success = self.classifier.predict(X)[0]
        success_proba = self.classifier.predict_proba(X)[0]
        classes = self.classifier.classes_.tolist()

        profit_log = float(self.regressor.predict(X)[0])
        estimated_profit = float(np.expm1(max(0.0, profit_log)))

        return {
            "success_level": success,
            "success_confidence": {label: float(prob) for label, prob in zip(classes, success_proba)},
            "estimated_profit_usd": estimated_profit,
        }

    def recommend(self, payload: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
        price = float(payload.get("price_usd", 0))
        low_price, high_price = self.metadata["high_success_price_band"]
        recommendations = []
        risks = []
        opportunities = []

        if price < low_price:
            recommendations.append(f"Consider premium positioning: high-performing games often price above ${low_price:.2f}.")
            opportunities.append("Room to increase ARPU by testing a slightly higher launch price.")
        elif price > high_price:
            recommendations.append(f"Price may be aggressive; strong performers often stay below ${high_price:.2f}.")
            risks.append("Higher price can suppress early conversion and review velocity.")
        else:
            recommendations.append("Price aligns with the high-success market band in this dataset.")
            opportunities.append("Pricing is in a historically strong conversion window.")

        platform_count = int(payload.get("platforms_win", 0)) + int(payload.get("platforms_mac", 0)) + int(
            payload.get("platforms_linux", 0)
        )
        if platform_count < 2:
            risks.append("Limited platform coverage can reduce discoverability and launch momentum.")
            recommendations.append("Add at least one more platform target to increase market reach.")
        else:
            opportunities.append("Multi-platform release can improve algorithmic visibility at launch.")

        tags = str(payload.get("tags", "")).lower()
        top_tags_text = " ".join(self.metadata["top_tags"]).lower()
        if tags and not any(tag in top_tags_text for tag in [t.strip() for t in tags.split(",") if t.strip()]):
            risks.append("Current tag strategy does not overlap strongly with high-frequency market tags.")
            recommendations.append("Blend niche tags with 2-3 mainstream tags to improve search visibility.")
        else:
            opportunities.append("Tag strategy has good alignment with high-performing market metadata.")

        selected_genres = [g.strip().lower() for g in str(payload.get("genres", "")).split(",") if g.strip()]
        top_genres = set(self.metadata.get("top_genres", []))
        if selected_genres and any(g in top_genres for g in selected_genres):
            opportunities.append("At least one selected genre aligns with top-performing Steam segments.")
        elif selected_genres:
            recommendations.append("Consider adding one trend-friendly genre blend to improve demand fit.")

        trend_alignment = "Strong" if prediction["success_level"] == "High Success" else "Moderate"
        if prediction["success_level"] == "Low Success":
            trend_alignment = "Weak"
            risks.append("Model predicts low success likelihood under current assumptions.")

        return {
            "trend_alignment": trend_alignment,
            "recommendations": recommendations,
            "risk_factors": risks,
            "opportunities": opportunities,
        }
