from openai import OpenAI
from notebook import Notebook
import json
from tool_registry import ToolRegistry
from notebook_wrapper import NotebookWrapper
import logging
from user_agent import UserAgent
import base_log
import os
from cwd import cwd

log = base_log.BASE_LOG.getChild(__name__)

class NotebookAgent:
    def __init__(self, agent_id):
        self.tr = ToolRegistry(agent_id)
        with cwd(os.path.join("tmp", agent_id)):
            self.nb = Notebook(agent_id)
        self.nbw = NotebookWrapper(self.nb)
        self.user_agent = UserAgent(agent_id)
        self.agent_id = agent_id

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
        instructions="You are a pro python coding agent. Use the provided functions create, edit and execute code in a python notebook. You are able to use juypter notebook to do any processing for the user. Make sure to display any generated files to the user. The use will be able to inspect and download a file after calling show_user_file, you should not link it in your response. If you find yourself doing too many tool calls ask the user for help.",
        model="gpt-4o-mini",
        tools=self.tr.tools)

        self.thread = self.client.beta.threads.create()


    def handle_tool_calls(self, tool_calls):
        tool_outputs = []
        for tool in tool_calls:
            func = self.tr.get_tool(tool.function.name)
            if not func:
                log.error(f"{self.agent_id}:Function {tool.function.name} is not registered.")
                raise ValueError(f"Function {tool.function.name} is not registered.")
            
            log.info(f"{self.agent_id}:Tool call -> {tool.function.name}")
            output = func(tool.function.arguments)
            if output:
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": str(output)
                })
        return tool_outputs
    
    def handle_user_input(self, user_input, attachments=None):
        context_text = ""
        if attachments:
            context_text += "(User has provided the following attachments, they are available to the jupyter notebook:"
            for attachment in attachments:
                # files.append({"file_id": self.client.files.create(file=open(attachment, "rb"), purpose="assistants").id, "tools": [{"type":"show_user_file"}]})
                context_text += f" {attachment}"
            context_text += ")"

        log.info(f"{self.agent_id}:User input -> {user_input}{(" " + " ".join(attachments)) if attachments else ''}")
        self.client.beta.threads.messages.create(thread_id=self.thread.id, role="user", content=context_text + user_input)
        run = self.client.beta.threads.runs.create_and_poll(thread_id=self.thread.id,assistant_id=self.assistant.id)
        num_retries = 0
        while run.status == 'requires_action':
            tool_outputs = self.handle_tool_calls(run.required_action.submit_tool_outputs.tool_calls)

            if tool_outputs:
                try:
                    run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(thread_id=self.thread.id, run_id=run.id, tool_outputs=tool_outputs)
                    log.debug(f"{self.agent_id}:Tool outputs submitted successfully.")
                except Exception as e:
                    log.error(f"{self.agent_id}:Failed to submit tool outputs:", e)
            else:
                log.debug(f"{self.agent_id}No tool outputs to submit.")
            
            status = run.status
            self.nbw.save("notebook.ipynb")
            num_retries += 1
            if num_retries > 30:
                log.error(f"{self.agent_id}:Exceeded max retries.")
                break

        self.nbw.save("notebook.ipynb")
        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            log.debug(f"{self.agent_id}:Run completed successfully. -> {messages.data[0].content[0].text.value}")
            return messages.data[0].content[0].text.value

        log.error(f"Unknown status: {status} - {run.last_error.code} - {run.last_error.message}")
        return {"error": f"Unknown status: {status} - {run.last_error.code} - {run.last_error.message}"}