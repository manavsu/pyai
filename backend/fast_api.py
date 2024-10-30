from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends, Response, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import os
import httpx
import uuid
from fastapi.middleware.cors import CORSMiddleware
from cluster import Cluster

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = open("openai_key.secret").read().strip()
cluster = Cluster(api_key=api_key)

@app.get("/")
async def index():
    return "Hello, World!"

@app.post("/new_agent/")
async def new_agent(response: Response):
    agent_id = "agent_" + str(uuid.uuid4())
    response.set_cookie(key="agent_id", value=agent_id)
    cluster.add_agent(agent_id)
    return {"message": "Agent created successfully.", "agent_id": agent_id}

@app.post("/query/")
async def query_agent(request: Request, query: str=Form(...), attachments: Optional[list[UploadFile]] = None):
    agent_id = request.cookies.get('agent_id')
    port = cluster.get_agent_port(agent_id)
    files = [('attachments', (file.filename, file.file.read(), file.content_type)) for file in attachments] if attachments else []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://localhost:{port}/query/", data={"query" : query}, files=files)
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_file/{filename}")
async def get_file(filename: str, request: Request):
    agent_id = request.cookies.get('agent_id')
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent id not found, try creating a new one.")

    safe_filename = os.path.basename(filename)
    file_path = os.path.join(os.getcwd(), "tmp", agent_id, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run the FastAPI app