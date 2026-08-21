import os
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
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

# In docker-compose, this will be http://model:8001
MODEL_URL = os.getenv("MODEL_URL", "http://localhost:8001")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
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
