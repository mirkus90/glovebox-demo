from typing import Any
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

current_temperature = 0.0
current_status = "running"

_machine_status_schema = {
    "type": "function",
    "name": "machine_status",
    "description": "Check the status of the Glovebox machine. Returns a value among 'running', 'stopped', 'error'",
    "parameters": {}
}

_machine_set_temperature_schema = {
    "type": "function",
    "name": "set_temperature",
    "description": "Set the temperature of the Glovebox machine using the input value.",
    "parameters": {
        "type": "object",
        "properties": {
            "input": {
                "type": "number",
                "description": "New temperature value to set for the Glovebox machine."
            }
        },
        "required": ["input"],
        "additionalProperties": False
    }
}

_machine_get_temperature_schema = {
    "type": "function",
    "name": "get_temperature",
    "description": "Get the current temperature of the Glovebox machine",
    "parameters": {}
}

async def _machine_status(args: Any) -> ToolResult:
    return ToolResult(current_status, ToolResultDirection.TO_SERVER)

async def _machine_set_temperature(args: Any) -> ToolResult:
    if not isinstance(args, dict) or "input" not in args:
        return ToolResult("error", ToolResultDirection.TO_SERVER)
    global current_temperature
    current_temperature = float(args["input"])
    return ToolResult(f"Temperature set to {current_temperature}", ToolResultDirection.TO_SERVER)

async def _machine_get_temperature(args: Any) -> ToolResult:
    return ToolResult(current_temperature, ToolResultDirection.TO_SERVER)


def attach_machine_tools(rtmt: RTMiddleTier) -> None:
    rtmt.tools["machine_status"] = Tool(schema=_machine_status_schema, target=lambda args: _machine_status(args))
    rtmt.tools["set_temperature"] = Tool(schema=_machine_set_temperature_schema, target=lambda args: _machine_set_temperature(args))
    rtmt.tools["get_temperature"] = Tool(schema=_machine_get_temperature_schema, target=lambda args: _machine_get_temperature(args))