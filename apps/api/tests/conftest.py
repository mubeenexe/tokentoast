"""Pytest fixtures for API tests. Run from apps/api with: pytest tests/ -v"""
import os

import pytest
import httpx
from httpx import ASGITransport

# Relax rate limits so tests don't get 429 (app reads these before first request)
os.environ.setdefault("RATE_LIMIT_REGISTER_PER_MINUTE", "100")
os.environ.setdefault("RATE_LIMIT_LOGIN_PER_MINUTE", "100")


@pytest.fixture(scope="session")
async def client():
    """Import app inside fixture so DB engine is created in the test event loop."""
    from main import app
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac
