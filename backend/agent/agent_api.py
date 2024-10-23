from fastapi import FastAPI
import uuid
import sys

app = FastAPI()

print(sys.argv)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.route('/new_agent/', methods=['POST'])
async def new_agent():
    agent_id = "agent_" + str(uuid.uuid4())
    print(f"Creating new agent with id: {agent_id}")
    if agent_manager.create_agent(agent_id):
        response = make_response(jsonify({"message":"Agent created successfully.", "agent_id": agent_id}))
        response.set_cookie('agent_id', agent_id)
        return response
    response = make_response(jsonify({"error": "Unable to create agent, try again."}), 400)
    return response

