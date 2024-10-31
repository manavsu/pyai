from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends, Response, Form
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from typing import Optional
import os
import httpx
import uuid
from fastapi.middleware.cors import CORSMiddleware
from cluster import Cluster
import base_log
import logging
import signal

log = base_log.BASE_LOG.getChild(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)s

api_key = open("openai_key.secret").read().strip()
cluster = Cluster(api_key=api_key)

@app.get("/")
async def index():
    return "Hello, World!"

@app.post("/new_agent/")
async def new_agent():
    agent_id = "agent_" + str(uuid.uuid4())
    log.info(f"Creating new agent with id: {agent_id}")
    cluster.add_agent(agent_id)
    return {"message": "Agent created successfully.", "agent_id": agent_id}

@app.post("/query/")
async def query_agent(agent_id: str=Form(...), query: str=Form(...), attachments: Optional[list[UploadFile]] = None):
    log.info(f"Querying agent with id: {agent_id}")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent id not found, try creating a new one.")
    port = cluster.get_agent_port(agent_id)
    files = [('attachments', (file.filename, file.file.read(), file.content_type)) for file in attachments] if attachments else []
    try:
        async with httpx.AsyncClient(timeout=240) as client:
            response = await client.post(f"http://localhost:{port}/query/", data={"query" : query}, files=files)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_file/{agent_id}/{filename}")
async def get_file(request: Request, agent_id:str, filename: str, ):
    log.info(f"Getting file: {filename}")
    port = cluster.get_agent_port(agent_id)
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent id not found, try creating a new one.")
 
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(f"http://localhost:{port}/get_file/{filename}")
            response.raise_for_status()
            path = response.content.decode().replace('"', '')
            if os.path.exists(path):
                return FileResponse(path=path, media_type="application/octet-stream", filename=filename)
            raise HTTPException(status_code=404, detail="File not found.")

    except Exception as e:
        log.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def signal_handler(sig, frame):
    print('Signal received, shutting down...')
    cluster.shutdown()

if __name__ == "__main__":
    import uvicorn
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run the FastAPI app