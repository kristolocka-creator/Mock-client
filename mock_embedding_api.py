import random
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class EmbedRequest(BaseModel):
    text: str


@app.post("/embed")
def embed(request: EmbedRequest, error: str = None):
    if error == "429":
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests"
        )

    if error == "500":
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

    if error == "503":
        raise HTTPException(
            status_code=503,
            detail="Service Unavailable"
        )

    if error == "timeout":
        time.sleep(6)

    embedding = [
        random.uniform(-1, 1)
        for _ in range(128)
    ]

    return {"embedding": embedding}