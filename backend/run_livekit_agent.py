"""Start the LiveKit interviewer agent worker (run from backend/)."""
from livekit.agents import cli

from services.interview.session.transport.agent import server

if __name__ == "__main__":
    cli.run_app(server)
