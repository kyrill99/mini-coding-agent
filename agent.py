import os
import subprocess
import json
from rich.console import Console
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True) 
openai = OpenAI() 
console = Console()

def show(text):
    try:
        console.print(text)
    except Exception:
        print(text)

# State variables for our plan
todos = []
completed = []


# Simple way to report on the status of our plan
def get_todo_report() -> str:
    result = ""
    for index, todo in enumerate(todos):
        if completed[index]:
            result += f"Todo #{index + 1}: [green][strike]{todo}[/strike][/green]\n" #
        else:
            result += f"Todo #{index + 1}: {todo}\n"
    show(result)
    return result

def create_todos(descriptions: list[str]) -> str:
    todos.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return get_todo_report()

def mark_complete(index: int, completion_notes: str) -> str:
    if 1 <= index <= len(todos):
        completed[index - 1] = True
    else:
        return "No todo at this index."
    console.print(f"[blue]Update:[/blue] {completion_notes}") 
    return get_todo_report()

# Tool functions that the agent can call
def read_file(filepath: str) -> str:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return f"Successfully read {filepath}:\n\n{content}"
    except Exception as e:
        return f"Error reading file {filepath}: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        show(f"[blue]Agent wrote to file:[/blue] {filepath}")
        return f"Successfully wrote to {filepath}."
    except Exception as e:
        return f"Error writing to {filepath}: {str(e)}"

def run_terminal_command(command: str) -> str:
    show(f"[yellow]Agent running command:[/yellow] {command}")
    try:
        # Run the command and capture stdout and stderr
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30 # Prevent infinite loops
        )
        
        output = f"Exit Code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
            
        return output
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Failed to execute command: {str(e)}"
    

#Json schemas for the agent's tool calls
# --- JSON Schemas ---
create_todos_json = {
    "name": "create_todos",
    "description": "Add new todos from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                "type": "array",
                "items": {"type": "string"},
                "title": "Descriptions"
            }
        },
        "required": ["descriptions"],
        "additionalProperties": False
    }
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the todo at the given position (starting from 1) and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "index": {
                "description": "The 1-based index of the todo to mark as complete",
                "title": "Index",
                "type": "integer"
            },
            "completion_notes": {
                "description": "Notes about how you completed the todo",
                "title": "Completion Notes",
                "type": "string"
            }
        },
        "required": ["index", "completion_notes"],
        "additionalProperties": False
    }
}

read_file_json = {
    "name": "read_file",
    "description": "Read the contents of a file at the specified filepath.",
    "parameters": {
        "type": "object",
        "properties": {
            "filepath": {"type": "string", "description": "The path to the file to read"}
        },
        "required": ["filepath"],
        "additionalProperties": False
    }
}

write_file_json = {
    "name": "write_file",
    "description": "Write content to a file, creating it or overwriting it.",
    "parameters": {
        "type": "object",
        "properties": {
            "filepath": {"type": "string", "description": "The path to the file"},
            "content": {"type": "string", "description": "The exact code/text to write to the file"}
        },
        "required": ["filepath", "content"],
        "additionalProperties": False
    }
}

run_terminal_command_json = {
    "name": "run_terminal_command",
    "description": "Run a shell command in the terminal. Returns stdout, stderr, and the exit code.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The shell command to execute (e.g., 'python script.py' or 'ls -la')"}
        },
        "required": ["command"],
        "additionalProperties": False
    }
}

# our list of tools that the agent can call, with their JSON schemas
tools = [
    {"type": "function", "function": create_todos_json},
    {"type": "function", "function": mark_complete_json},
    {"type": "function", "function": read_file_json},
    {"type": "function", "function": write_file_json},
    {"type": "function", "function": run_terminal_command_json}
]

# The Tool Router
def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # This dynamically finds the Python function by its string name!
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        
        results.append({
            "role": "tool",
            "content": json.dumps(result),
            "tool_call_id": tool_call.id
        })
    return results

# The main loop that runs the agent until completion
def loop(messages):
    done = False
    while not done:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
        )
        finish_reason = response.choices[0].finish_reason
        
        if finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
            
    show(response.choices[0].message.content)

# --- Run the Agent ---
system_message = """
You are an autonomous software engineering agent.
When given a task, you must follow this exact workflow:
1. Use `create_todos` to plan the steps required to complete the task.
2. Use `write_file` to write the necessary code.
3. Use `run_terminal_command` to test your code to ensure it works. 
4. If a test fails, read the error output, use `write_file` to fix the code, and test it again.
5. Use `mark_complete` to check off steps in your plan as you finish them successfully.
6. Do not stop until the final code runs perfectly without errors. Reply with a final summary only when finished.
"""

# this is an example, but you can just run the agent and give it any task you want in the terminal!
example_user_message = """
Write a Python script called 'math_utils.py' that contains a function to calculate the factorial of a number.
Then, write a script called 'test.py' that imports this function, runs it for the number 5, and prints the result.
Run 'test.py' to verify it outputs 120.
"""

messages = [
    {"role": "system", "content": system_message}, 
    {"role": "user", "content": example_user_message}
]

if __name__ == "__main__":
    show("[bold green]Starting Autonomous Agent...[/bold green]")
    # Prompt the user for their task directly in the terminal!
    user_task = console.input("[bold cyan]What would you like the agent to build today?[/bold cyan]\n> ")
    
    messages = [
        {"role": "system", "content": system_message}, 
        {"role": "user", "content": user_task}
    ]
    
    show("\n[bold yellow]Agent is analyzing the request and planning...[/bold yellow]")
    loop(messages)