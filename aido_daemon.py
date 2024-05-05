import os
import json
import socket
import re
from _thread import start_new_thread
from mlx_lm import load, generate

llm_model = "mistralai/Mistral-7B-Instruct-v0.2"
llm_model_context_length = 32 * 1024
aigo_work_dir = os.environ.get("AIGO_WORK_DIR", os.getcwd())

llm_system_prompt_focus = """
You are an assistant trained to help users focus on a specific project based on their current working environment and command history. Below, you will find a snapshot of the current directory structure and a history of recent relevant commands. Based on this information and the user's query, please identify the most relevant project focus and return only relevant project path.
Do not add any additional information to the response. Do not use any markdown formatting.
Correct response example looks like this:

Focus: some/path/to/project
Suggestions: some suggestions


If the user doesn't provide any specific project context, set the focus to None and provide suggestions based on the user query.
There should be only one focus suggestion.
---
"""

llm_system_prompt_intent = """
You are an assistant specialized in understanding software development environments and providing precise operational commands or guidance based on user queries. Below, you will find detailed information about a specific project, including its directory structure, configuration files like 'package.json', 'Makefile', and 'docker-compose.yml', as well as content from 'README.md'.

Given this detailed project context and the user's query, please provide a direct command that the user can execute to accomplish their goal, or guide them on the steps they should take next.
Do not use any markdown formatting.

Correct response example looks like this:

Command: some/path/to/project
Suggestions: some suggestions


If the user is not in the correct directory, prepend the command with the correct cd command to navigate to the project directory.
There should be only one command suggestion.
Respond as briefly as possible, focusing on the most relevant action. Add suggestions only if necessary, otherwise set to None.

Project Details:

"""


def get_suggestions(model, tokenizer, input_text):
    response = generate(
        model,
        tokenizer,
        prompt=input_text,
        verbose=True,
        max_tokens=500
    )

    print(response)
    return response


def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""


def get_directory_snapshot(current_path, depth=3):
    snapshot = []
    for root, dirs, files in os.walk(current_path, topdown=True):
        level = root.replace(current_path, '').count(os.sep)
        indent = ' ' * 2 * level

        if level < depth:
            dirs[:] = [d for d in dirs]
        else:
            dirs[:] = []

        if '.git' in dirs:
            snapshot.append(f"{indent}{os.path.abspath(root)}/")
            
            for f in files:
                snapshot.append(f"{indent}  {f}")
    
    return "\n".join(snapshot)

def get_package_scripts(package_json_path):
    try:
        with open(package_json_path, 'r') as file:
            data = json.load(file)
            return data.get("scripts", {})
    except FileNotFoundError:
        return {}


def create_project_context(project_path):
    context = []

    # Contents of the project directory
    context.append(f"\nContents of the project directory ({project_path}):")
    project_contents = os.listdir(project_path)
    context.extend(project_contents)

    # Contents of the readme file
    readme_path = os.path.join(project_path, "README.md")
    readme_content = read_file_content(readme_path)
    if readme_content:
        context.append(f"\nReadme content:\n\n{readme_content}")

    # Contents of package.json (scripts)
    package_json_path = os.path.join(project_path, "package.json")
    package_scripts = get_package_scripts(package_json_path)
    if package_scripts:
        context.append("\nPackage.json scripts:\n")
        context.extend(package_scripts.keys())

    # Contents of docker-compose.yml
    docker_compose_path = os.path.join(project_path, "docker-compose.yml")
    docker_compose_content = read_file_content(docker_compose_path)
    if docker_compose_content:
        context.append("\nDocker-compose.yml content:\n")
        context.append(docker_compose_content)

    # Contents of Makefile
    makefile_path = os.path.join(project_path, "Makefile")
    makefile_content = read_file_content(makefile_path)
    if makefile_content:
        context.append("\nMakefile content:\n")
        context.append(makefile_content)

    return "\n".join(context)


def parse_user_intent_response(text):
    command_pattern = r"Command:\s*(.+)"
    suggestions_pattern = r"Suggestions:\s*(.+)"

    command_match = re.search(command_pattern, text)
    suggestions_match = re.search(suggestions_pattern, text)

    command = None if command_match and command_match.group(1).strip() == 'None' else command_match.group(1).strip() if command_match else None
    suggestions = None if suggestions_match and suggestions_match.group(1).strip() == 'None' else suggestions_match.group(1).strip() if suggestions_match else None

    return {
        'command': command and command.replace("\t", "").replace("\n", ""),
        'suggestions': suggestions and suggestions.replace("None. ", "")
    }


def parse_focus_response(text):
    focus_pattern = r"Focus:\s*(.+)"
    suggestions_pattern = r"Suggestions:\s*(.+)"

    suggestions_regex = re.compile(suggestions_pattern, re.DOTALL)

    focus_match = re.search(focus_pattern, text)
    suggestions_match = re.search(suggestions_regex, text)

    focus = None if focus_match and focus_match.group(1).strip() == 'None' else focus_match.group(1).strip() if focus_match else None
    suggestions = None if suggestions_match and suggestions_match.group(1).strip() == 'None' else suggestions_match.group(1).strip() if suggestions_match else None

    return {
        'focus': focus and focus.replace("\t", "").replace("\n", ""),
        'suggestions': suggestions and suggestions.replace("None. ", "")
    }


def get_initial_project_focus(user_input, context, model, tokenizer) -> dict:
    """Determines the project focus based on initial context and user input."""
   
    full_prompt = f"{llm_system_prompt_focus}\n\nDirectory Context:\n{context}\n\nUser Query: {user_input}\n\n"
    
    # Get suggestions from the AI model
    project_focus_suggestions = get_suggestions(model, tokenizer, full_prompt)
    parsed_focus_suggestions = parse_focus_response(project_focus_suggestions)

    return parsed_focus_suggestions


def infer_user_intent(project_path, current_dir, user_query, model, tokenizer) -> dict:
    """Infers the user's intent based on a detailed project context and provides a direct command or guidance."""

    project_context = create_project_context(project_path)
    
    full_prompt = f"\
    {llm_system_prompt_intent}\n\n\
    {project_context}\n\n\n\
    Current directory: {current_dir}\n\n\
    User Query: {user_query}\n\n\n\
    "

    # Get suggestions from the AI model
    action_suggestions = get_suggestions(model, tokenizer, full_prompt)
    parsed_action_suggestions = parse_user_intent_response(action_suggestions)

    return parsed_action_suggestions


def load_history():
    history_path = os.path.join(os.environ.get("HOME"), ".zsh_history")
    irrelevant_prefixes = {
        'ls', 'cd', 'docker', 'mkdir', 'echo', 'cat', 'ps', 'pwd', 'clear', 'exit',
        'man', 'kill', 'top', 'htop', 'chmod', 'chown', 'cp', 'mv', 'rm', 'touch',
        'df', 'du', 'history', 'who', 'wget', 'curl', 'scp', 'ssh', 'ping', 'tar'
    }
    unique_commands = set()

    try:
        with open(history_path, 'r') as file:
            for line in file:
                # Extract command after the last semicolon
                parts = line.strip().rsplit(';', 1)
                if len(parts) > 1:
                    command = parts[-1].strip()
                    if not any(command.startswith(prefix) for prefix in irrelevant_prefixes):
                        unique_commands.add(command)
    except FileNotFoundError:
        print("Zsh history file not found.")
        return ""

    return '\n'.join(unique_commands)

def get_context(cwd):
    directory_context = get_directory_snapshot(cwd)
    # history_context = load_history()

    return f"{directory_context}\n"
    # return f"{directory_context}\n{history_context}"

def get_model():
    model, tokenizer = load(llm_model)
    
    return model, tokenizer
    
def setup_socket_server():
    host = 'localhost'
    port = int(os.environ.get("AIGO_PORT", 9999))
    
    print(f"Starting server on {host}:{port}...")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"Listening on {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")
        start_new_thread(client_handler, (client_socket,))


def client_handler(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            print(f"Received data: {data}")

            user_query, current_dir = parse_data(data)
            
            print(f"Current directory: {current_dir}")
            print(f"User query: {user_query}")
            
            initial_context = get_context(aigo_work_dir)

            print("Determining initial project focus...")
            project_focus_suggestion = get_initial_project_focus(user_query, initial_context, model, tokenizer)

            if not project_focus_suggestion["focus"]:
                print("No project focus found.")
                response = format_socket_request("None", project_focus_suggestion["suggestions"])
                print(f"Sending response: {response}")
                client_socket.sendall(response.encode('utf-8'))

                break
            
            print("Infering user intent...")
            intent_response = infer_user_intent(project_focus_suggestion["focus"], current_dir, user_query, model, tokenizer)
            
            print(f"Sending response: {intent_response}")
            client_socket.sendall(
                format_socket_request(intent_response["command"], intent_response["suggestions"]).encode('utf-8')
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            client_socket.sendall(format_socket_request("None", "An error occurred").encode('utf-8'))
            break
    client_socket.close()

def format_socket_request(command, suggestion):
    return f"{command}|{suggestion}"
    # return f"{command}|{suggestion}|{context}"


def parse_data(data):
    # split the data into a list, first element is the user query and the second is current directory
    data = data.split('|')
    return data[0], data[1]

if __name__ == "__main__":
    model, tokenizer = get_model()
    setup_socket_server()