import json
class UserAgent():
    def __init__(self):
        self.notifications = []

    def show_user_file(self, file_path):
        """Display the contents of a file to the user.

        Args:
            file_path (string): The path to the file to be displayed.
        """
        self.notifications.append({"type": "file", "file_path": file_path})
        return "Contents of the file displayed."

    def show_user_file_wrapper(self, args):
        args = json.loads(args)
        return self.show_user_file(args['file_path'])

