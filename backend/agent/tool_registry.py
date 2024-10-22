from tool_definition_generator import *
from notebook import Notebook

class ToolRegistry:
    def __init__(self):
        self.tools = []
        self.tool_map = {}

    def register_tool(self, function, wrapper):
        tool_definition = create_tool_definition(function)
        self.tools.append(tool_definition)
        self.tool_map[tool_definition["function"]["name"]] = wrapper

    def get_tool(self, name):
        return self.tool_map.get(name)
    