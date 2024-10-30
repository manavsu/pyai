from fastapi import FastAPI, File, UploadFile, Form, Request, Response, HTTPException
from fastapi.responses import FileResponse
import uuid
from typing import Optional, List
import sys
import os
from agent_manager import AgentManager
from threading import Event
import asyncio
import signal
import base_log

log = base_log.BASE_LOG.getChild(__name__)

if len(sys.argv) < 4:
    print("Usage: python fast_api.py <port> <api_key> <agent_id> <log_path>")
    sys.exit(1)

port = int(sys.argv[1])
api_key = sys.argv[2]
agent_id = sys.argv[3]


app = FastAPI()

agent_manager = AgentManager(api_key=api_key, agent_id=agent_id)

@app.get("/")
async def root():
    return {"message": agent_id}

@app.post("/query/")
async def query(query: str = Form(...), attachments: Optional[list[UploadFile]] = None):
    log.info(f"{agent_id}:Querying agent with id: {agent_id}")
    uploaded_attachments = []
    if attachments:
        for file in attachments:
            log.info(f"{agent_id}:Saving attachment: {file.filename}")
            agent_manager.save_attachment(file)
            uploaded_attachments.append(file.filename)
    try:
        message = agent_manager.query_agent(query, attachments=(uploaded_attachments if uploaded_attachments else None))
        notifications = agent_manager.get_notifications()
    except ValueError as e:
        raise HTTPException(status_code=400, detail="An error occurred while querying agent")

    return {"message": message, "notifications": notifications}

@app.get('/get_file/<filename>/')
async def get_file(filename):
    safe_filename = os.path.basename(filename)
    log.info(f"{agent_id}:Getting file: {safe_filename}")

    if not os.path.exists(safe_filename):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(path=safe_filename, media_type="application/octet-stream", filename=filename)


if __name__ == "__main__":
    import uvicorn
    
    loop = asyncio.get_event_loop()

    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)

    def sig_handler(sig, frame):
        loop.create_task(server.shutdown())
    
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    loop.run_until_complete(server.serve())
