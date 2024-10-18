import os

import httpx


def read_file(path: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, path)

    with open(file_path, "r") as file:
        content = file.read()
    return content


def make_stream_response(content: str) -> httpx.Response:
    return httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content=content,
    )
