import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
import os
import re
from openai import OpenAI
from openai._streaming import Stream
from openai.types.chat import ChatCompletionChunk
from typing import AsyncIterable

if "PERPLEXITY_API_KEY" in os.environ:
    api_key = os.environ["PERPLEXITY_API_KEY"]
else:
    raise SystemExit("PERPLEXITY_API_KEY not found in environment variables")

debug = os.environ.get("GPTSCRIPT_DEBUG", "false") == "true"

client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

app = FastAPI()

def log(*args):
    if debug:
        print(*args)

@app.get("/")
async def get_root():
    return "ok"

# The perplexity API does not have a method to list models, so we are hard coding the models here
@app.get("/v1/models")
async def list_models() -> JSONResponse:
    return JSONResponse(content={"data": [
        {"id": "sonar-small-chat", "name": "Perplexity Sonar Small Chat"},
        {"id": "sonar-small-online", "name": "Perplexity Sonar Small Online"},
        {"id": "sonar-medium-chat", "name": "Perplexity Sonar Medium Chat"},
        {"id": "sonar-medium-online", "name": "Perplexity Sonar Medium Online"}
    ]})

@app.post("/v1/chat/completions")
async def completions(request: Request) -> StreamingResponse:
    try:
        data = await request.json()
        model = data.get("model")
        messages = data.get("messages")

        if model is None:
            raise HTTPException(status_code=400, detail="Unable to identify a model.")
        if messages is None:
            raise HTTPException(status_code=400, detail="Unable to identify messages.")

        try:
            res = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
        except Exception as e:
            log("Error getting a response from Perplexity.", e)
            raise HTTPException(status_code=500, detail="Error getting a response from Perplexity.")

        return StreamingResponse(convert_stream(res), media_type="application/x-ndjson")
    
    except Exception as e:
        log("An unexpected error occurred.", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def convert_stream(stream: Stream[ChatCompletionChunk]) -> AsyncIterable[str]:
    for chunk in stream:
        log("CHUNK: ", chunk.model_dump_json())
        yield "data: " + str(chunk.model_dump_json()) + "\n\n"
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
                log_level="debug" if debug else "critical", reload=debug, access_log=debug)