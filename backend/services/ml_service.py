"""ML inference service for empirical Bengaluru Traffic Pulse dataset predictions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = REPO_ROOT / "backend" / "models" / "bangalore_traffic_ml.joblib"
STATS_PATH = REPO_ROOT / "backend" / "models" / "corridor_stats.json"


class BangaloreMLService:
    """Provides empirical ML predictions and historical statistics from 8,936 Bengaluru observations."""

    def __init__(self):
        self._model_data: Optional[Dict[str, Any]] = None
        self._stats_data: Optional[List[Dict[str, Any]]] = None

    def _load(self):
        if self._model_data is None and MODEL_PATH.exists():
            self._model_data = joblib.load(MODEL_PATH)
        if self._stats_data is None and STATS_PATH.exists():
            with open(STATS_PATH, "r", encoding="utf-8") as f:
                self._stats_data = json.load(f)

    def is_ready(self) -> bool:
        self._load()
        return self._model_data is not None

    def get_corridor_stats(self) -> List[Dict[str, Any]]:
        self._load()
        return self._stats_data or []

    def get_metadata(self) -> Dict[str, Any]:
        self._load()
        if not self._model_data:
            return {}
        return {
            "areas": self._model_data.get("areas", []),
            "roads": self._model_data.get("roads", []),
            "weather_conditions": self._model_data.get("weather_conditions", []),
            "roadwork_options": self._model_data.get("roadwork_options", ["No", "Yes"]),
            "top_features": self._model_data.get("top_features", {}),
            "dataset_rows": 8936,
        }

    def predict(
        self,
        area_name: str,
        road_name: str,
        traffic_volume: float = 30000.0,
        incident_reports: int = 1,
        weather_condition: str = "Clear",
        roadwork: str = "No",
    ) -> Dict[str, Any]:
        self._load()
        if not self._model_data:
            raise RuntimeError("Bangalore ML model artifact not loaded.")

        feature_names = self._model_data["feature_names"]
        df_input = pd.DataFrame(0, index=[0], columns=feature_names)

        df_input["Traffic Volume"] = float(traffic_volume)
        df_input["Incident Reports"] = int(incident_reports)

        area_col = f"Area Name_{area_name}"
        if area_col in feature_names:
            df_input[area_col] = 1

        road_col = f"Road/Intersection Name_{road_name}"
        if road_col in feature_names:
            df_input[road_col] = 1

        weather_col = f"Weather Conditions_{weather_condition}"
        if weather_col in feature_names:
            df_input[weather_col] = 1

        roadwork_col = f"Roadwork and Construction Activity_{roadwork}"
        if roadwork_col in feature_names:
            df_input[roadwork_col] = 1

        models = self._model_data["models"]
        pred_cong = float(models["congestion"].predict(df_input)[0])
        pred_util = float(models["utilization"].predict(df_input)[0])
        pred_tti = float(models["tti"].predict(df_input)[0])
        pred_speed = float(models["speed"].predict(df_input)[0])

        # Clamp physically reasonable bounds
        pred_cong = max(0.0, min(100.0, round(pred_cong, 1)))
        pred_util = max(0.0, min(100.0, round(pred_util, 1)))
        pred_tti = max(1.0, min(2.5, round(pred_tti, 2)))
        pred_speed = max(5.0, min(100.0, round(pred_speed, 1)))

        # Find historical corridor stats
        corridor_stat = None
        if self._stats_data:
            corridor_stat = next(
                (s for s in self._stats_data if s["area"] == area_name and s["road"] == road_name),
                None,
            )

        return {
            "area_name": area_name,
            "road_name": road_name,
            "inputs": {
                "traffic_volume": traffic_volume,
                "incident_reports": incident_reports,
                "weather_condition": weather_condition,
                "roadwork": roadwork,
            },
            "predictions": {
                "congestion_level_pct": pred_cong,
                "capacity_utilization_pct": pred_util,
                "travel_time_index": pred_tti,
                "predicted_speed_kmph": pred_speed,
            },
            "historical_baseline": corridor_stat,
            "model_provenance": "Random Forest Regressor trained on 8,936 Kaggle Bengaluru observations (R²=0.964)",
        }


ml_service = BangaloreMLService()

