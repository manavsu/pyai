from fastapi import FastAPI, File, UploadFile, Form, Request, Response, HTTPException
import uuid
from typing import Optional, List
import sys
import os
from agent_manager import AgentManager

app = FastAPI()

print(sys.argv)

AGENT_ID = uuid.uuid4() # TODO

agent_manager = AgentManager()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/query/")
async def query(query: str = Form(...), attachments: Optional[list[UploadFile]] = File(None)):
    if attachments:
        for file in attachments:
            agent_manager.save_attachment(file)
    
    try:
        message = agent_manager.query_agent(query, attachments=[file.filename for file in attachments])
        notifications = agent_manager.get_notifications()
    except ValueError as e:
        raise HTTPException(status_code=400, detail="An error occurred while querying agent")

    return {"message": message, "notifications": notifications}

@app.route('/get_file/<filename>', methods=['GET'])
def get_file(filename):
    safe_filename = os.path.basename(filename)
    return send_file(os.path.join(os.getcwd(),"tmp", agent_id, safe_filename))
