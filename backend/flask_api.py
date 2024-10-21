from flask import Flask, request, jsonify, send_from_directory, make_response, send_file
from flask_cors import CORS
import logging
import uuid
from agent_manager import AgentManager
import os
import shutil

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

agent_manager = AgentManager()
# if os.path.exists("tmp"):
#     shutil.rmtree("tmp")

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/new_agent/', methods=['POST'])
def new_agent():
    agent_id = "agent_" + str(uuid.uuid4())
    print(f"Creating new agent with id: {agent_id}")
    if agent_manager.create_agent(agent_id):
        response = make_response(jsonify({"message":"Agent created successfully.", "agent_id": agent_id}))
        response.set_cookie('agent_id', agent_id)
        return response
    response = make_response(jsonify({"error": "Unable to create agent, try again."}), 400)
    return response


@app.route('/query/', methods=['POST'])
def query():
    agent_id = request.cookies.get('agent_id')
    print(f"Querying agent with id: {agent_id}")
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

@app.route('/get_file/<filename>', methods=['GET'])
def get_file(filename):
    agent_id = request.cookies.get('agent_id') #TODO: add indiviudal .venvs
    safe_filename = os.path.basename(filename)
    return send_file(os.path.join(os.getcwd(),"tmp", agent_id, safe_filename))

if __name__ == '__main__':
    app.run(debug=True)