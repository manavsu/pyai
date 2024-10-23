from tool_definition_generator import *
from notebook import Notebook
import base_log

log = base_log.BASE_LOG.getChild(__name__)

class ToolRegistry:
    def __init__(self, agent_id):
        self.tools = []
        self.tool_map = {}
        self.agent_id = agent_id

    def register_tool(self, function, wrapper):
        tool_definition = create_tool_definition(function)
        self.tools.append(tool_definition)
        self.tool_map[tool_definition["function"]["name"]] = wrapper
        log.debug(f"{self.agent_id}:Tool registered: {tool_definition['function']['name']}")

    def get_tool(self, name):
        log.debug(f"{self.agent_id}:Retrieving tool: {name}")
        return self.tool_map.get(name)
    