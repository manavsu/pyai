from notebook_agent import NotebookAgent

class AgentManager:
    def __init__(self, api_key, agent_id):
        self.agent = NotebookAgent(api_key=api_key, agent_id=agent_id)
    
    def query_agent(self,user_input, attachments=None):
        if not user_input:
            raise ValueError("User input cannot be empty.")
        return self.agent.handle_user_input(user_input, attachments)
        
    def save_attachment(self, file):
        with open(file.filename, "wb") as f:
            f.write(file.file.read())
    
    def get_notifications(self):
        notifications = self.agent.user_agent.notifications
        self.agent.user_agent.notifications = []
        return notifications