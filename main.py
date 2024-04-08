import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import os
from openai import OpenAI
from openai._streaming import Stream
from openai.types.chat import ChatCompletionChunk
from typing import AsyncIterable

debug = os.environ.get("GPTSCRIPT_DEBUG", "false") == "true"

app = FastAPI()

url = "https://api.perplexity.ai/chat/completions"

if "PERPLEXITY_API_KEY" in os.environ:
    api_key = os.environ["PERPLEXITY_API_KEY"]
else:
    raise SystemExit("PERPLEXITY_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

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
    data = await request.body()
    data = json.loads(data)
    print("Request: ", request)
    print("Data: ", data)
    messages = [
        {
            "role": "system",
            "content": (
                "Be precise and concise. Only print maximum 5 words."
            ),
        },
        {
            "role": "user",
            "content": (
                "How many stars are in the universe?"
            ),
        },
    ]
    
    res = client.chat.completions.create(
        model="sonar-small-chat",
        messages=messages,
        stream=True
    )

    return StreamingResponse(convert_stream(res), media_type="application/x-ndjson")

async def convert_stream(stream: Stream[ChatCompletionChunk]) -> AsyncIterable[str]:
    for chunk in stream:
        print("CHUNK: ", chunk.json())
        yield "data: " + str(chunk.json()) + "\n\n"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
                log_level="debug" if debug else "critical", reload=debug, access_log=debug)