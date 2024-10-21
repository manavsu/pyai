from agent import NotebookAgent
class AgentManager:
    def __init__(self):
        self.agents = {}
    
    def create_agent(self, agent_id):
        if agent_id in self.agents:
            return False
        self.agents[agent_id] = NotebookAgent()
        return True
    
    def query_agent(self, agent_id, user_input):
        if agent_id not in self.agents:
            raise ValueError("Agent not found.")
        if not user_input:
            raise ValueError("User input cannot be empty.")
        return self.agents[agent_id].handle_user_input(user_input)
    
    def get_notifications(self, agent_id):
        if agent_id not in self.agents:
            raise ValueError("Agent not found.")
        return self.agents[agent_id].user_agent.notifications