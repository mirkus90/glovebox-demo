import logging
import os
from typing import Any
import aiohttp

from utils import decode_url_string
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

logger = logging.getLogger("voiceassistant")

_todolist_create_task_name_schema = {
    "type": "function",
    "name": "todolist_create_task",
    "description": "Create a task based on the user request. Never ask the user about the session_id. Before running this tool, make sure to repeat the collected text. Ask the user to confirm the action, then proceed with the execution of the API",
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "The session ID used to identify the file to be modified.",
            },
            "text": {
                "type": "string",
                "description": "The actual text of the task to be created"
            }
        },
        "required": ["session_id", "text"]
    }
}

async def _create_task(args: Any) -> ToolResult:
    """
    Create a task based on the input provided by the user on a Google Task related to the current session.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                # Decode the API URL from environment variable in case it's base64 encoded
                decode_url_string(os.environ.get("TODOLIST_CREATE_TASK_API_URL")),
                json={
                    "taskList": args["session_id"], # the session ID is used as task list name
                    "taskTitle": "Created by Glovebox Assistant",
                    "taskText": args["text"]
                }
            ) as response:
                response.raise_for_status()
            return ToolResult(f"Task created successfully", ToolResultDirection.TO_SERVER)
    except Exception as e:
        logger.error(f"An error occurred while creating the task: {str(e)}")
        return ToolResult(f"An error occurred while creating the task. Please try again later.", ToolResultDirection.TO_SERVER)

    
def attach_todolist_tools(
        rtmt: RTMiddleTier) -> None:
    rtmt.tools["todolist_create_task"] = Tool(schema=_todolist_create_task_name_schema, target=lambda args: _create_task(args))