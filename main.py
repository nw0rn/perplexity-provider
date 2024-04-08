import json
from typing import Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import os
from openai import OpenAI
import requests

debug = os.environ.get("GPTSCRIPT_DEBUG", "false") == "true"

app = FastAPI()

url = "https://api.perplexity.ai/chat/completions"

# if "PERPLEXITY_API_KEY" in os.environ:
#     api_key = os.environ["PERPLEXITY_API_KEY"]
# else:
#     raise SystemExit("PERPLEXITY_API_KEY not found in environment variables")

api_key = "123"

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
        payload = {
            "model": "sonar-small-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise. Only print maximum 5 words."
                },
                {
                    "role": "user",
                    "content": "How many stars are there in our galaxy?"
                }
            ]
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response code is not 2xx

        print(response.text)
        return StreamingResponse(content=response.text, media_type="application/json")

    except requests.RequestException as e:
        # Handles exceptions raised by the requests library
        error_message = e.response.text if hasattr(e, "response") and e.response else str(e)
        raise HTTPException(status_code=500, detail="Internal server error occurred. Error message: " + error_message + request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
                log_level="debug" if debug else "critical", reload=debug, access_log=debug)