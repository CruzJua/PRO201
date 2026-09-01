"""CRUD repositories for the Supabase application tables."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from supabase import Client

from .client import create_supabase_client


class UsersRepository:
    def __init__(self, client: Client):
        self.client = client

    def create(self, user_id: int, name: str) -> dict[str, Any]:
        return self.client.table("Users").insert({"user_id": user_id, "name": name}).execute().data[0]

    def get(self, user_id: int) -> dict[str, Any] | None:
        rows = self.client.table("Users").select("*").eq("user_id", user_id).limit(1).execute().data
        return rows[0] if rows else None

    def list(self) -> list[dict[str, Any]]:
        return self.client.table("Users").select("*").order("user_id").execute().data

    def update(self, user_id: int, name: str) -> dict[str, Any] | None:
        rows = self.client.table("Users").update({"name": name}).eq("user_id", user_id).execute().data
        return rows[0] if rows else None

    def delete(self, user_id: int) -> bool:
        return bool(self.client.table("Users").delete().eq("user_id", user_id).execute().data)


class ImagesRepository:
    def __init__(self, client: Client):
        self.client = client

    def create(self, image_id: int, url: str) -> dict[str, Any]:
        return self.client.table("Images").insert({"image_id": image_id, "url": url}).execute().data[0]

    def get(self, image_id: int) -> dict[str, Any] | None:
        rows = self.client.table("Images").select("*").eq("image_id", image_id).limit(1).execute().data
        return rows[0] if rows else None

    def list(self) -> list[dict[str, Any]]:
        return self.client.table("Images").select("*").order("image_id").execute().data

    def update(self, image_id: int, url: str) -> dict[str, Any] | None:
        rows = self.client.table("Images").update({"url": url}).eq("image_id", image_id).execute().data
        return rows[0] if rows else None

    def delete(self, image_id: int) -> bool:
        return bool(self.client.table("Images").delete().eq("image_id", image_id).execute().data)


class PredictionsRepository:
    def __init__(self, client: Client):
        self.client = client

    def create(self, pred_id: int, user_id: str, image_id: int, description: str) -> dict[str, Any]:
        return self.client.table("Prediction").insert(
            {
                "pred_id": pred_id,
                "user_id": user_id,
                "image_id": image_id,
                "description": description,
            }
        ).execute().data[0]

    def get(self, pred_id: int) -> dict[str, Any] | None:
        rows = self.client.table("Prediction").select("*").eq("pred_id", pred_id).limit(1).execute().data
        return rows[0] if rows else None

    def list(self) -> list[dict[str, Any]]:
        return self.client.table("Prediction").select("*").order("pred_id").execute().data

    def list_by_user(self, user_id: str) -> list[dict[str, Any]]:
        """Return all predictions for a given Supabase auth user, newest first.

        `user_id` is the auth UUID (the JWT `sub` claim), not a `Users.user_id`.
        """
        rows = self.client.table("Prediction").select(
            "pred_id, description, Images!inner(url)"
        ).eq("user_id", user_id).order("pred_id", desc=True).execute().data
        return [
            {
                "pred_id": row["pred_id"],
                "label": row["description"],
                "image_url": row["Images"]["url"],
            }
            for row in rows
        ]

    def update(self, pred_id: int, description: str) -> dict[str, Any] | None:
        rows = self.client.table("Prediction").update({"description": description}).eq("pred_id", pred_id).execute().data
        return rows[0] if rows else None

    def delete(self, pred_id: int) -> bool:
        return bool(self.client.table("Prediction").delete().eq("pred_id", pred_id).execute().data)

    def list_with_user_and_image(self) -> list[dict[str, Any]]:
        """Return every prediction joined with its image URL.

        `Prediction.user_id` now holds a Supabase auth UUID rather than a
        `Users.user_id`, so there is no longer a foreign key to embed a user
        name through — the raw `user_id` is returned instead.
        """
        rows = self.client.table("Prediction").select(
            "pred_id, user_id, description, Images!inner(url)"
        ).order("pred_id").execute().data
        return [
            {
                "pred_id": row["pred_id"],
                "user_id": row["user_id"],
                "url": row["Images"]["url"],
                "description": row["description"],
            }
            for row in rows
        ]


class Database:
    """Application-facing collection of repositories."""

    def __init__(self, client: Client | None = None):
        supabase = client or create_supabase_client()
        self.client = supabase
        self.users = UsersRepository(supabase)
        self.images = ImagesRepository(supabase)
        self.predictions = PredictionsRepository(supabase)

    def check_connection(self) -> bool:
        """Verify credentials and access to the application database."""
        self.client.table("Users").select("user_id").limit(1).execute()
        return True


@lru_cache(maxsize=1)
def get_database() -> Database:
    """Return the process-wide database instance configured from the environment."""
    return Database()