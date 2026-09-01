import os
import secrets
import time
import uuid
import httpx
import boto3
import jwt
from jwt import PyJWKClient
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Backend API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_URL = os.getenv("MODEL_URL", "http://localhost:8001")
SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL")

# R2 config
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "brain")
R2_PUBLIC_DOMAIN = os.getenv("NEXT_PUBLIC_IMAGE_DOMAIN", "")

_jwks_client = PyJWKClient(SUPABASE_JWKS_URL) if SUPABASE_JWKS_URL else None

# Supabase DAL — import lazily so missing env vars don't crash startup
_db = None


def get_db():
    global _db
    if _db is None:
        try:
            import sys, pathlib
            # Make the sibling `database` package importable
            repo_root = pathlib.Path(__file__).resolve().parent.parent
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))
            from database import get_database
            _db = get_database()
        except Exception as exc:
            print(f"[warn] Could not initialise database DAL: {exc}")
    return _db


def _r2_client():
    """Return a boto3 S3 client pointed at Cloudflare R2."""
    endpoint = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def _public_url(object_key: str) -> str:
    """Build the browser-facing URL for an uploaded object.

    A custom domain or r2.dev domain serves objects from the bucket root, but the
    S3 API endpoint is path-style and needs the bucket name in the path.
    """
    base = R2_PUBLIC_DOMAIN.rstrip("/")
    if "r2.cloudflarestorage.com" in base:
        return f"{base}/{R2_BUCKET_NAME}/{object_key}"
    return f"{base}/{object_key}"


def _new_id() -> int:
    """Generate a time-ordered bigint primary key.

    `pred_id` and `image_id` are bigint with no sequence default, so the id has
    to come from the application. Basing it on the clock keeps ids sortable, so
    ordering by `pred_id` descending really does mean newest-first on the
    history page; the random low digits avoid collisions inside one tick.
    """
    return time.time_ns() // 1000 * 1000 + secrets.randbelow(1000)


async def require_auth(authorization: str = Header(...)) -> dict:
    if _jwks_client is None:
        raise HTTPException(status_code=500, detail="Authentication not configured on this server.")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header must use the Bearer scheme.")
    token = authorization.removeprefix("Bearer ")
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=[signing_key.algorithm_name],
            options={"verify_aud": False},
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.exceptions.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    user: dict = Depends(require_auth),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()

    # 1. Get prediction from model service
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, image_bytes, file.content_type)}
            response = await client.post(f"{MODEL_URL}/predict", files=files)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            prediction = response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error connecting to model service: {exc}")

    # 2. Upload image to R2 (best-effort — never fail the request)
    r2_url = None
    try:
        if R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY and R2_ACCOUNT_ID:
            ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg"
            object_key = f"predictions/{uuid.uuid4()}.{ext}"
            s3 = _r2_client()
            s3.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=object_key,
                Body=image_bytes,
                ContentType=file.content_type,
            )
            r2_url = _public_url(object_key)
        else:
            print("[warn] R2 credentials not configured — skipping image upload.")
    except Exception as exc:
        print(f"[warn] R2 upload failed: {exc}")

    # 3. Save to Supabase (best-effort — never fail the request)
    try:
        db = get_db()
        user_sub = user.get("sub")
        if db and r2_url and user_sub:
            img_id = _new_id()
            db.images.create(image_id=img_id, url=r2_url)
            db.predictions.create(
                pred_id=_new_id(),
                user_id=user_sub,
                image_id=img_id,
                description=prediction.get("predicted_label", "unknown"),
            )
    except Exception as exc:
        print(f"[warn] Supabase save failed: {exc}")

    # Always return the prediction — storage failures are non-blocking
    return {
        **prediction,
        "image_url": r2_url,
    }


@app.get("/predictions")
async def list_predictions(user: dict = Depends(require_auth)):
    """Return the prediction history for the authenticated user."""
    try:
        db = get_db()
        user_sub = user.get("sub")
        if db is None or not user_sub:
            return {"predictions": []}
        return {"predictions": db.predictions.list_by_user(user_sub)}
    except Exception as exc:
        print(f"[warn] Could not fetch predictions: {exc}")
        return {"predictions": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
