from openai import OpenAI
from notebook import Notebook
import json
from tool_registry import ToolRegistry
from notebook_wrapper import NotebookWrapper
import logging
from user_agent import UserAgent

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class NotebookAgent:
    def __init__(self):
        self.tr = ToolRegistry()
        self.nb = Notebook()
        self.nbw = NotebookWrapper(self.nb)
        self.user_agent = UserAgent()

        self.tr.register_tool(self.nb.create_cell, self.nbw.create_cell)
        self.tr.register_tool(self.nb.edit_cell, self.nbw.edit_cell)
        self.tr.register_tool(self.nb.get_cell_content, self.nbw.get_cell_content)
        self.tr.register_tool(self.nb.delete_cell, self.nbw.delete_cell)
        self.tr.register_tool(self.nb.insert_cell, self.nbw.insert_cell)
        self.tr.register_tool(self.nb.install_package, self.nbw.install_package)
        self.tr.register_tool(self.nb.execute_all_cells, self.nbw.execute_all_cells)

        self.tr.register_tool(self.user_agent.show_user_file, self.user_agent.show_user_file_wrapper)

        key = open("openai_key.secret", "r").read().strip()
        self.client = OpenAI(api_key=key)

        self.assistant = self.client.beta.assistants.create(
        instructions="You are a pro python coding agent. Use the provided functions create, edit and execute code in a python notebook. You are able to use juypter notebook to do any processing for the suer. Make sure to display any generated files to the user.",
        model="gpt-4o-mini",
        tools=self.tr.tools)

        self.thread = self.client.beta.threads.create()


    def handle_tool_calls(self, tool_calls):
        tool_outputs = []
        for tool in tool_calls:
            func = self.tr.get_tool(tool.function.name)
            if not func:
                raise ValueError(f"Function {tool.function.name} is not registered.")
            
            output = func(tool.function.arguments)
            if output:
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": str(output)
                })
            print(f"tool call : {tool} -> {output}")
        return tool_outputs
    
    def handle_user_input(self, user_input):
        self.client.beta.threads.messages.create(thread_id=self.thread.id, role="user", content=user_input)
        run = self.client.beta.threads.runs.create_and_poll(thread_id=self.thread.id,assistant_id=self.assistant.id)
        
        while run.status == 'requires_action':
            tool_outputs = self.handle_tool_calls(run.required_action.submit_tool_outputs.tool_calls)

            if tool_outputs:
                try:
                    run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(thread_id=self.thread.id, run_id=run.id, tool_outputs=tool_outputs)
                    log.debug("Tool outputs submitted successfully.")
                except Exception as e:
                    log.error("Failed to submit tool outputs:", e)
            else:
                log.debug("No tool outputs to submit.")
            
            status = run.status
            self.nbw.save("tmp/test.ipynb")

        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            return messages.data[0].content[0].text.value

        log.error(f"Unknown status: {status} - {run.last_error.code} - {run.last_error.message}")
        return {"error": f"Unknown status: {status} - {run.last_error.code} - {run.last_error.message}"}


agent = NotebookAgent()
while True:
    user_input = input("--> ")
    if user_input == "exit":
        break

    print(agent.handle_user_input(user_input))