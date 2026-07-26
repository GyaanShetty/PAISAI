"""The PAISAI HTTP API (FastAPI).

This layer exposes the integrity core and calculation engine over HTTP, and — most
importantly — installs the Provenance & Validation Middleware that enforces the
no-hallucination policy at the boundary: a response carrying a numeric that is not
wrapped in a provenance envelope never leaves the server.
"""

from .app import create_app

__all__ = ["create_app"]
