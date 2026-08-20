"""Application Fit — job posting vs candidate evidence scoring.

Owns: extract/evidence/scoring pipeline, Fit snapshots, `/application-fit` service layer.
Does not own: live interview session, Signal readiness, generic LLM JSON helpers.
Entry: ApplicationFitService
"""

from services.application_fit.service import ApplicationFitService

__all__ = ["ApplicationFitService"]
