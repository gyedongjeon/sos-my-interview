"""Where the app keeps its files. The desktop shell overrides these through the environment."""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Everything the app stores: the database, recordings, and the voice model and cache.
DATA_DIR = Path(os.environ.get("SOS_MY_INTERVIEW_DATA_DIR") or BACKEND_DIR / "data")

# The built frontend (`npm run build`), served by the backend when it exists.
FRONTEND_DIST = Path(os.environ.get("SOS_MY_INTERVIEW_FRONTEND_DIST") or BACKEND_DIR.parent / "frontend" / "dist")
