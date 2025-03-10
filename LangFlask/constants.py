# constants.py
import json
import os

FILE_PATH = "constants.json"

# Initialize the file with a default value
def initialize_file():
    with open(FILE_PATH, "w") as f:
        json.dump({"restart_wordlist": False}, f)

# Get the current value of the shared variable
def get_shared_variable():
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/{FILE_PATH}", "r") as f:
        data = json.load(f)
        return data["restart_wordlist"]

# Update the shared variable
def set_shared_variable(new_value):
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/{FILE_PATH}", "w") as f:
        json.dump({"restart_wordlist": new_value}, f)

if __name__ == "__main__":
    initialize_file()
