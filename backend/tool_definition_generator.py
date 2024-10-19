import re 

def split_docstring(docstring):
    split = [s.strip() for s in docstring.strip().split("\n")]
    return [s for s in split if s]

def create_tool_definition(func: callable) -> dict:
    """Create an OpenAI tool definition from a function.

    Args:
        func (function): The function to create a tool definition for.

    Raises:
        ValueError: If the function does not have a docstring.

    Returns:
        dict: The tool definition.
    """

    tool_def = {"type": "function", "function": {}}
    function_def = tool_def["function"]
    function_def["name"] = func.__name__
    docs = split_docstring(func.__doc__)
    if not func.__doc__:
        raise ValueError("Function does not have a docstring.")
    
    function_def["description"] = docs[0]

    if len(docs) > 1:
            if any(line.startswith("Args:") for line in docs):
                function_def["parameters"] = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
                parameters = function_def["parameters"]
                args_section = False
                for line in docs:
                    line = line.strip()
                    if line.startswith("Args:"):
                        args_section = True
                        continue
                    if line.startswith("Returns:"):
                        args_section = False
                    if args_section:
                        match = re.match(r'^(\w+) \(([^)]+)\): (.+)$', line)
                        if match:
                            arg_name, arg_type, arg_description = match.groups()
                            parameters["properties"][arg_name] = {"type": arg_type, "description": arg_description}
                            parameters["required"].append(arg_name)

    return tool_def



def example_function(a, b):
    """
    Adds two numbers together.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of the two numbers.
    """
    return a + b

