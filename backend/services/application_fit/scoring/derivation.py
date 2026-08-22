"""Shared Application Fit band helpers."""

from __future__ import annotations

from services.application_fit.models import FitBand
from services.application_fit.weights import (
    FIT_BAND_COMPETITIVE_MIN,
    FIT_BAND_STRETCH_MIN,
    FIT_BAND_STRONG_MIN,
)


def fit_band_from_score(score: int) -> FitBand:
    if score >= FIT_BAND_STRONG_MIN:
        return "strong"
    if score >= FIT_BAND_COMPETITIVE_MIN:
        return "competitive"
    if score >= FIT_BAND_STRETCH_MIN:
        return "stretch"
    return "long_shot"
