"""
Vercel serverless entrypoint for the FastAPI auth API.
The API app is copied to api_backend/ at build time (see vercel.json buildCommand).
"""
import os
import sys

# Add api_backend so "from app.main import app" resolves (app is at api_backend/app)
_api_backend = os.path.join(os.path.dirname(__file__), "..", "api_backend")
sys.path.insert(0, _api_backend)

from app.main import app
