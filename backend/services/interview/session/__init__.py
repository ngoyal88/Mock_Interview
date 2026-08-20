"""Shared interview session machinery (lifecycle, persistence, runtime, transport, coding).

Owns: Redis session RMW, completion, question runtime, LiveKit agent, WS fallback, coding submit.
Does not own: mode-specific start inputs (see modes/) or Application Fit extraction.
"""
