"""Supabase client configuration."""

import os

from supabase import Client, create_client


def create_supabase_client() -> Client:
    """Create a Supabase client from the process environment."""
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SECRET_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )

    if not url:
        raise RuntimeError("SUPABASE_URL is not configured")
    if not key:
        raise RuntimeError(
            "SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY, or SUPABASE_KEY is not configured"
        )

    return create_client(url, key)