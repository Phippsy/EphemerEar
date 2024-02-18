def add_todo(text, todo_file="bots/donbot/output/responses/todos/todos.md"):
    """
    Adds a new todo item to the end of the 'todos.md' markdown file.

    Parameters:
    text (str): The task description to be added to the todo list.

    Returns:
    None: This function doesn't return any value. It simply appends the text to the file.
    """
    import os
    if not os.path.exists(os.path.dirname(todo_file)):
        os.makedirs(os.path.dirname(todo_file))
    if not os.path.exists(todo_file):
        with open(todo_file, "w") as file:
            file.write("# To-Do List\n\n")
    with open(todo_file, "a") as file:
        file.write(text + "\n")
    return f"Added the following to-do item to your list: {text}"

add_todo_definition = {
            "name": "add_todo",
            "description": "This function adds a to-do item to the user's todos.md file with the provided text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text of the to-do item to add. Be sure to use markdown formatting (e.g. use \"- [ ]\" for a checkbox, and other styling, for each item."
                    }
                },
                "required": ["text"]
            }
        }

def commit_to_memory(text, memory_file="bots/donbot/output/responses/todos/memory.md"):
    """
    Commits a new memory to the 'memory.md' markdown file.

    Parameters:
    text (str): The content to be added to the memory file.

    Returns:
    None: This function doesn't return any value. It simply appends the text to the file.
    """
    import os
    if not os.path.exists(os.path.dirname(memory_file)):
        os.makedirs(os.path.dirname(memory_file))
    if not os.path.exists(memory_file):
        with open(memory_file, "w") as file:
            file.write("# Memories\n\n")
    with open(memory_file, "a") as file:
        file.write(text + "\n")
    return f"Added the following memory to your list: {text}"

commit_to_memory_definition = {
            "name": "commit_to_memory",
            "description": "This function commits a piece of text to the user's memory.md markdown file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content to commit to memory. You can use markdown styling to format the memory entry."
                    }
                },
                "required": ["text"]
            }
        }