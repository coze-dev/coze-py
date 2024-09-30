import os


def read_file(path: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, path)

    with open(file_path, "r") as file:
        content = file.read()
    return content
