from openai import OpenAI
from tool_definition_generator import create_tool_definition
from notebook import Notebook, OutputType
import json
from tool_registry import ToolRegistry
from notebook_wrapper import NotebookWrapper
import logging

log = logging.getLogger(__name__)

tr = ToolRegistry()
nb = Notebook()
nbw = NotebookWrapper(nb)

tr.register_tool(nb.create_cell, nbw.create_cell)
tr.register_tool(nb.edit_cell, nbw.edit_cell)
tr.register_tool(nb.get_cell_content, nbw.get_cell_content)
tr.register_tool(nb.delete_cell, nbw.delete_cell)
tr.register_tool(nb.insert_cell, nbw.insert_cell)
tr.register_tool(nb.install_package, nbw.install_package)
tr.register_tool(nb.execute_all_cells, nbw.execute_all_cells)

print(tr.tools)

key = open("openai_key.secret", "r").read().strip()
client = OpenAI(api_key=key)

assistant = client.beta.assistants.create(
  instructions="You are a pro python coding agent. Use the provided functions create, edit and execute code in a python notebook. You are adept at working with Jupyter notebooks. The user can view the notebook.",
  model="gpt-4o-mini",
  tools=tr.tools
)

thread = client.beta.threads.create()

print("-_- Hello, I am a python coder. I can help you write, edit and execute python code.")

def handle_tool_calls(tool_calls):
    tool_outputs = []
    for tool in tool_calls:
        print(tool)
        func = tr.get_tool(tool.function.name)
        if not func:
            raise ValueError(f"Function {tool.function.name} is not registered.")
        
        output = func(tool.function.arguments)
        print(output)
        if output:
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": str(output)
            })
        nbw.save("test.ipynb")
    log.debug("Tool outputs:", tool_outputs)
    return tool_outputs

def main():
    status = 'input'
    while True:
        match status:
            case 'input':
                user_input = input("--> ")
                if user_input == "exit":
                    exit(0)
                client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_input)
                run = client.beta.threads.runs.create_and_poll(thread_id=thread.id,assistant_id=assistant.id)
                status = run.status
                print(status)
            case 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                if messages.data[0].content:
                    try:
                        print(messages.data[0].content[0].text.value)
                    except:
                        log.debug(messages.data[0].content)
                else:
                    log.debug(messages)
                status = 'input'
            case 'requires_action':
                tool_outputs = handle_tool_calls(run.required_action.submit_tool_outputs.tool_calls)

                if tool_outputs:
                    try:
                        run = client.beta.threads.runs.submit_tool_outputs_and_poll(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)
                        log.debug("Tool outputs submitted successfully.")
                    except Exception as e:
                        log.error("Failed to submit tool outputs:", e)
                else:
                    log.debug("No tool outputs to submit.")
                
                status = run.status
                nbw.save("test.ipynb")
            case _:
                log.error(f"Unknown status: {status}")
                log.debug(f"{run.last_error.code} - {run.last_error.message}")
                status = 'input'

main()