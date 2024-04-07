import json
from typing import Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()


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

# @app.post("/v1/chat/completions")
# async def completions(request: Request) -> StreamingResponse:

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")),
                log_level="debug" if debug else "critical", reload=debug, access_log=debug)