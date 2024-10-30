from agent import NotebookAgent
from cwd import cwd
import os

class AgentManager:
    def __init__(self):
        self.agents = {}
    
    # def create_agent(self, agent_id):
    #     if agent_id in self.agents:
    #         return False
    #     self.agents[agent_id] = NotebookAgent(agent_id)
    #     return True
    
    def query_agent(self, agent_id, user_input, attachments=None):
        if agent_id not in self.agents:
            raise ValueError("Agent not found.")
        if not user_input:
            raise ValueError("User input cannot be empty.")
        with cwd(os.path.join("tmp", agent_id)):
            return self.agents[agent_id].handle_user_input(user_input, attachments)
        
    def save_attachment(self, agent_id, file):
        if agent_id not in self.agents:
            raise ValueError("Agent not found.")
        with cwd(os.path.join(agent_id)):
            file.save(file.filename)
    
    # def get_notifications(self, agent_id):
    #     if agent_id not in self.agents:
    #         raise ValueError("Agent not found.")
    #     notifications = self.agents[agent_id].user_agent.notifications
    #     self.agents[agent_id].user_agent.notifications = []
    #     return notifications