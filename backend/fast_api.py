from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
from agent_manager import AgentManager
import uuid
from fastapi.middleware.cors import CORSMiddleware
import base_log

log = base_log.BASE_LOG.getChild(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager()

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/new_agent/', methods=['POST'])
def new_agent():
    agent_id = "agent_" + str(uuid.uuid4())
    log.info(f"Creating new agent with id: {agent_id}")
    if agent_manager.create_agent(agent_id):
        response = make_response(jsonify({"message":"Agent created successfully.", "agent_id": agent_id}))
        return response
    response = make_response(jsonify({"error": "Unable to create agent, try again."}), 400)
    return response


@app.route('/query/<agent_id>/', methods=['POST'])
def query(agent_id):
    log.info(f"Querying agent with id: {agent_id}")
    if not agent_id:
        return jsonify({"error": "Agent id not found, try creating a new one."}), 400
    
    attachments = request.files.getlist('files')
    for attachment in attachments:
        agent_manager.save_attachment(agent_id, attachment)

    try:
        message = agent_manager.query_agent(agent_id, request.form.get('input'), attachments=[attachment.filename for attachment in attachments])
        notifications = agent_manager.get_notifications(agent_id)
    except ValueError as e:
        return jsonify({"error":"An error occurred while querying agent"}), 400
    
    return jsonify({"message": message, "notifications": notifications})

@app.route('/get_file/<agent_id>/<filename>/', methods=['GET'])
def get_file(agent_id, filename):
    log.info(f"Getting file: {filename}")
    safe_filename = os.path.basename(filename)
    return send_file(os.path.join(os.getcwd(),"tmp", agent_id, safe_filename))

app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")