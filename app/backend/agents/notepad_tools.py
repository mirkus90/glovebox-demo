import logging
import os
from typing import Any
import aiohttp

from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
from utils import decode_url_string, is_float

logger = logging.getLogger("voiceassistant")
temperature_param = "temperature"
hours_param = "hours"

_notepad_save_note_name_schema = {
    "type": "function",
    "name": "notepad_save_note",
    "description": "Save the note provided by the user. The note must be a string. Never ask the user about the session_id. Before running this tool, make sure to repeat the collected text. Ask the user to confirm the action, then proceed with the execution of the API",
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "The session ID used to identify the file to be modified.",
            },
            "text": {
                "type": "string",
                "description": "The actual text of the note to be saved"
            }
        },
        "required": ["session_id", "text"]
    }
}

_notepad_modify_file_schema = {
    "type": "function",
    "name": "notepad_modify_file",
    "description": "Modify a text file by replacing all occurrences of temperature and hours. Before running this tool, make sure to repeat the collected parameters. Ask the user to confirm the action, then proceed with the execution of the API",
    "parameters": {
        "type": "object",
        "properties": {
            "fileName": {
                "type": "string",
                "description": "The name of the text file to be modified."
            },
            "temperature": {
                "type": "string",
                "description": "The value of temperature to be replaced in the file"
            },
            "hours": {
                "type": "string",
                "description": "The number of hours to be replaced in the file"
            }
        },
        "required": ["fileName"]
    }
}

_notepad_get_file_name_schema = {
    "type": "function",
    "name": "notepad_get_file_name",
    "description": "Get the file name using the text provided by the user. " + \
                    "If the user provided a number as keyword, be sure to use the digit representation of the number, not the string. " + \
                    "For example, if the user provided 10, use 10, not ten.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "A keyword within the file name."
            }
        },
        "required": ["text"]
    }
}

async def _save_note(args: Any) -> ToolResult:
    """
    Save the note provided by the user on a file related to the current session.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                # Decode the API URL from environment variable in case it's base64 encoded
                decode_url_string(os.environ.get("NOTEPAD_APPEND_FILE_CONTENT_API_URL")),
                json={
                    "baseUrl": os.environ.get("NOTEPAD_BASE_URL"),
                    "fileName": f"{args["session_id"]}.txt", # the session ID is used as the file name
                    "text": args["text"]
                }
            ) as response:
                response.raise_for_status()
            return ToolResult(f"Note saved successfully", ToolResultDirection.TO_SERVER)
    except Exception as e:
        logger.error(f"An error occurred while modifying the file: {str(e)}")
        return ToolResult(f"An error occurred while modifying the file. Please try again later.", ToolResultDirection.TO_SERVER)


async def _modify_text_file(args: Any) -> ToolResult:
    """
    Modify a text file by replacing all occurrences of oldText with newText.
    """
    if (args.get(temperature_param) is None) and (args.get(hours_param) is None):
        return ToolResult("No parameters provided to modify the file. Please retry", ToolResultDirection.TO_SERVER)
    if args.get(temperature_param) is None:
        if args.get(hours_param, "").isdigit():
            # pattern xh means "x" hours
            oldText = "xh"
            newText = f"{args[hours_param]}h"
        else:
            return ToolResult("No valid parameter provided for the hours. Please retry", ToolResultDirection.TO_SERVER)
    elif args.get(hours_param) is None:
        if is_float(args.get(temperature_param, "")):
            # pattern yC means "y" degrees Celsius
            oldText = "yC"
            newText = f"{args[temperature_param]}C"
        else:
            return ToolResult("No valid parameter provided for the temperature. Please retry", ToolResultDirection.TO_SERVER)
    else:
        if args[hours_param].isdigit() and is_float(args[temperature_param]):
            oldText = "xhyC"
            newText = f"{args[hours_param]}h{args[temperature_param]}C"        
        else:
            return ToolResult("No valid parameter provided for temperature and hours. Please retry", ToolResultDirection.TO_SERVER)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                # Decode the API URL from environment variable in case it's base64 encoded
                decode_url_string(os.environ.get("NOTEPAD_REPLACE_FILE_CONTENT_API_URL")),
                json={
                    "filePath": f"{os.environ.get('NOTEPAD_BASE_URL')}/{args['fileName']}",
                    "oldText": oldText,
                    "newText": newText
                }
            ) as response:
                response.raise_for_status()
        return ToolResult(f"File modified successfully", ToolResultDirection.TO_SERVER)
    except Exception as e:
        logger.error(f"An error occurred while modifying the file: {str(e)}")
        return ToolResult(f"An error occurred while modifying the file: {str(e)}", ToolResultDirection.TO_SERVER)
    
async def _get_file_name(args: Any) -> ToolResult:
    """
    Get the file name of a text file using the input provided by the user.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                # Decode the API URL from environment variable in case it's base64 encoded
                decode_url_string(os.environ.get("NOTEPAD_GET_FILE_NAME_API_URL")),
                json={
                    "baseUrl": os.environ.get("NOTEPAD_BASE_URL"),
                    "text": args["text"].lower()
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if not data or "fileName" not in data or data["fileName"] == None:
                    return ToolResult("No file name found. Please retry", ToolResultDirection.TO_SERVER)
                return ToolResult(data["fileName"], ToolResultDirection.TO_SERVER)
    except Exception as e:
        logger.error(f"An error occurred while retrieving the file name: {str(e)}")
        return ToolResult(f"An error occurred while retrieving the file name. Please try again later.", ToolResultDirection.TO_SERVER)

    
def attach_notepad_tools(rtmt: RTMiddleTier) -> None:
    rtmt.tools["notepad_modify_file"] = Tool(schema=_notepad_modify_file_schema, target=lambda args: _modify_text_file(args))
    rtmt.tools["notepad_get_file_name"] = Tool(schema=_notepad_get_file_name_schema, target=lambda args: _get_file_name(args))
    rtmt.tools["notepad_save_note"] = Tool(schema=_notepad_save_note_name_schema, target=lambda args: _save_note(args))