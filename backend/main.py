import os
import httpx
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

_jwks_client = PyJWKClient(SUPABASE_JWKS_URL) if SUPABASE_JWKS_URL else None


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
    _user: dict = Depends(require_auth),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()

    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, image_bytes, file.content_type)}
            response = await client.post(f"{MODEL_URL}/predict", files=files)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error connecting to model service: {exc}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
