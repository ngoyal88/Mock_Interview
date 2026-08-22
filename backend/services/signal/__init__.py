"""Signal Intelligence — readiness scoring from vault, VPM, and interview history.

Owns: readiness compute/history (`/signal/readiness/*`).
Does not own: Application Fit adjudication, interview session runtime.
Entry: compute_readiness, get_readiness_history
"""

from services.signal.readiness_service import compute_readiness, get_readiness_history

__all__ = ["compute_readiness", "get_readiness_history"]
