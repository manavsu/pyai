from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends, Response, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import os
from agent_manager import AgentManager
import uuid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager()

@app.get("/")
async def index():
    return "Hello, World!"


@app.post("/new_agent/")
async def new_agent(response: Response):
    agent_id = "agent_" + str(uuid.uuid4())
    response.set_cookie(key="agent_id", value=agent_id)
    return {"message": "Agent created successfully.", "agent_id": agent_id}

# @app.post("/query/")
# async def query(query: str = Form(...), attachments: Optional[list[UploadFile]] = None):
#     log.info(f"{agent_id}:Querying agent with id: {agent_id}")
#     uploaded_attachments = []
#     if attachments:
#         for file in attachments:
#             log.info(f"{agent_id}:Saving attachment: {file.filename}")
#             agent_manager.save_attachment(file)
#             uploaded_attachments.append(file.filename)
#     try:
#         message = agent_manager.query_agent(query, attachments=(uploaded_attachments if uploaded_attachments else None))
#         notifications = agent_manager.get_notifications()
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail="An error occurred while querying agent")

#     return {"message": message, "notifications": notifications}

@app.post("/query/")
async def query_agent(request: Request, query: str=Form(...), attachments: Optional[list[UploadFile]] = None):
    agent_id = request.cookies.get('agent_id')
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent ID not found, try creating a new one.")

    # Save attachments
    print(f"Received {len(attachments)} attachments")
    for attachment in attachments:
        print(f"Saving attachment: {attachment.filename}")
        save_path = os.path.join(os.getcwd(), "tmp", agent_id, attachment.filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(await attachment.read())

    try:
        form_data = await request.form()
        message = agent_manager.query_agent(agent_id, form_data.get('input'), attachments=[attachment.filename for attachment in attachments])
        notifications = agent_manager.get_notifications(agent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": message, "notifications": notifications}

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
