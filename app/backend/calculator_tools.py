from typing import Any
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

_multiply_tool_schema = {
    "type": "function",
    "name": "multiply",
    "description": "Multiply two numbers and provide the result",
    "parameters": {
        "type": "object",
        "properties": {
            "A": {
                "type": "number",
                "description": "The first number to multiply"
            },
            "B": {
                "type": "number",
                "description": "The second number to multiply"
            }
        },
        "required": ["A", "B"],
        "additionalProperties": False
    }
}

async def _multiply_tool(args: Any) -> ToolResult:
    print(f"Multiplying {args['A']} and {args['B']}")
    return ToolResult(args["A"] * args["B"], ToolResultDirection.TO_SERVER)

def attach_calculator_tools(rtmt: RTMiddleTier) -> None:
    rtmt.tools["multiply"] = Tool(schema=_multiply_tool_schema, target=lambda args: _multiply_tool(args))