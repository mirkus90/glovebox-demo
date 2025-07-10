from typing import Any
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

_calculator_add_tool_schema = {
    "type": "function",
    "name": "calculator_add",
    "description": "Add two numbers and provide the result",
    "parameters": {
        "type": "object",
        "properties": {
            "A": {
                "type": "number",
                "description": "The first number to add"
            },
            "B": {
                "type": "number",
                "description": "The second number to add"
            }
        },
        "required": ["A", "B"],
        "additionalProperties": False
    }
}

_calculator_subtract_tool_schema = {
    "type": "function",
    "name": "calculator_subtract",
    "description": "Subtract two numbers and provide the result",
    "parameters": {
        "type": "object",
        "properties": {
            "A": {
                "type": "number",
                "description": "The first number to subtract from"
            },
            "B": {
                "type": "number",
                "description": "The second number to subtract"
            }
        },
        "required": ["A", "B"],
        "additionalProperties": False
    }
}

_calculator_multiply_tool_schema = {
    "type": "function",
    "name": "calculator_multiply",
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

_calculator_divide_tool_schema = {
    "type": "function",
    "name": "calculator_divide",
    "description": "Divide two numbers and provide the result, with floating point precision",
    "parameters": {
        "type": "object",
        "properties": {
            "A": {
                "type": "number",
                "description": "The numerator"
            },
            "B": {
                "type": "number",
                "description": "The denominator"
            }
        },
        "required": ["A", "B"],
        "additionalProperties": False
    }
}

async def _add_tool(args: Any) -> ToolResult:
    print(f"Adding {args['A']} and {args['B']}")
    return ToolResult(args["A"] + args["B"], ToolResultDirection.TO_SERVER)

async def _subtract_tool(args: Any) -> ToolResult:
    print(f"Subtracting {args['B']} from {args['A']}")
    return ToolResult(args["A"] - args["B"], ToolResultDirection.TO_SERVER)

async def _multiply_tool(args: Any) -> ToolResult:
    print(f"Multiplying {args['A']} and {args['B']}")
    return ToolResult(args["A"] * args["B"], ToolResultDirection.TO_SERVER)

async def _divide_tool(args: Any) -> ToolResult:
    if args["B"] == 0:
        return ToolResult("Division by zero error", ToolResultDirection.TO_SERVER)
    print(f"Dividing {args['A']} by {args['B']}")
    result = float(args["A"]) / float(args["B"])
    return ToolResult(result, ToolResultDirection.TO_SERVER)

def attach_calculator_tools(rtmt: RTMiddleTier) -> None:
    rtmt.tools["calculator_add"] = Tool(schema=_calculator_add_tool_schema, target=lambda args: _add_tool(args))
    rtmt.tools["calculator_subtract"] = Tool(schema=_calculator_subtract_tool_schema, target=lambda args: _subtract_tool(args))
    rtmt.tools["calculator_multiply"] = Tool(schema=_calculator_multiply_tool_schema, target=lambda args: _multiply_tool(args))
    rtmt.tools["calculator_divide"] = Tool(schema=_calculator_divide_tool_schema, target=lambda args: _divide_tool(args))