import json
import base_log
import os

log = base_log.BASE_LOG.getChild(__name__)

class UserAgent():
    def __init__(self, agent_id):
        self.notifications = []
        self.agent_id = agent_id

    def show_user_file(self, file_path):
        """Display the contents of a file to the user. The user will be able to inspect and download the file. You should not link it in your response.

        Args:
            file_path (string): The path to the file to be displayed.
        """
        if not os.path.exists(file_path):
            log.info(f"{self.agent_id}:File not found: {file_path}")
            return "File not found."
        self.notifications.append({"type": "file", "content": file_path})
        log.info(f"{self.agent_id}:Displaying file: {file_path}")
        return "Contents of the file displayed."

    def show_user_file_wrapper(self, args):
        args = json.loads(args)
        return self.show_user_file(args['file_path'])

