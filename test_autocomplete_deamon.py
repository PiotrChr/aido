import time
from aido_daemon import (
    load_history,
    get_directory_snapshot,
    get_context,
    get_initial_project_focus,
    get_model,
    create_project_context,
    infer_user_intent
)

cwd = "/Users/piotrchrusciel/Documents/Work/Programming"
project_cwd = "/Users/piotrchrusciel/Documents/Work/Programming/portfolio-v6"
user_query = "start portfolio-v6"

# print("\nLoading history...\n")
# start_time = time.time()
# history = load_history()
# print(f"History loaded in {time.time() - start_time:.2f} seconds\n")

# print("\nGetting directory snapshot...\n")
# start_time = time.time()
# snapshot = get_directory_snapshot(cwd)
# print(f"Directory snapshot taken in {time.time() - start_time:.2f} seconds\n")

# print("\nCreating context...\n")
# start_time = time.time()
# context = get_context(cwd)
# print(f"Context created in {time.time() - start_time:.2f} seconds\n")

print("\nLoading model and tokenizer...\n")
start_time = time.time()
model, tokenizer = get_model()
print(f"Model and tokenizer loaded in {time.time() - start_time:.2f} seconds\n")

# print("\nDetermining initial project focus...\n")
# start_time = time.time()
# project_focus_suggestions = get_initial_project_focus(user_query, context, model, tokenizer)
# print(f"Initial project focus determined in {time.time() - start_time:.2f} seconds\n")

print("\nCreating project context...\n")
start_time = time.time()
project_context = create_project_context(project_cwd)
print(f"Project context created in {time.time() - start_time:.2f} seconds\n")

print("\nTesting infer_user_intent for 'start portfolio-v6'...\n")
start_time = time.time()
user_intent = infer_user_intent(project_cwd, "start portfolio-v6", model, tokenizer)
print(f"Inference for 'start portfolio-v6' completed in {time.time() - start_time:.2f} seconds\n")

print("\nTesting infer_user_intent for 'stop portfolio-v6'...\n")
start_time = time.time()
user_intent = infer_user_intent(project_cwd, "stop portfolio-v6", model, tokenizer)
print(f"Inference for 'stop portfolio-v6' completed in {time.time() - start_time:.2f} seconds\n")

print("\nTesting infer_user_intent for 'install dependencies for portfolio-v6'...\n")
start_time = time.time()
user_intent = infer_user_intent(project_cwd, "install dependencies for portfolio-v6", model, tokenizer)
print(f"Inference for 'install dependencies' completed in {time.time() - start_time:.2f} seconds\n")
