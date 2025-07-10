from typing import Any
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
from models.junior import JuniorMachineState, Deck, PositionReading

# Simulated Junior machine state
# In a real-world scenario, this would interface with actual hardware or a database.
# For this example, we will simulate the machine's state with simple variables.
# These variables would be replaced with actual hardware interaction code.
# For example, you might use a library to communicate with the machine's API or hardware interface.

# Simulated current state of the Junior machine with a global variable so that multiple sessions can access it
global current_junior_state
current_junior_state = JuniorMachineState(
    decks=[
        Deck(
            name="1",
            positions=[
                PositionReading(name="1", setpoint=0.0,   temperature=27.2),
                PositionReading(name="2", setpoint=0.1,   temperature=27.3),
            ],
        ),
        Deck(
            name="2",
            positions=[
                PositionReading(name="1", setpoint=0.0,   temperature=27.1),
                PositionReading(name="2", setpoint=100.0, temperature=100.0),
            ],
        ),
    ]
)

param_deck = "deck"
param_position = "position"
param_setpoint = "setpoint"

_machine_get_status_schema = {
    "type": "function",
    "name": "machine_get_status",
    "description": "Check the status of the machine. " + \
                    "Deck and position names are used to identify the machine's state. " + \
                    "Both are numbers. Be sure to use the digit representation of the number, not the string. " + \
                    "For example, if the user provided 10, use 10, not ten." + \
                    "The machine can have multiple decks, each with multiple positions. ",
    "parameters": {
        "type": "object",
        "properties": {
            "deck": {
                "type": "string",
                "description": "The name of the deck."
            },
            "position": {
                "type": "string",
                "description": "The name of the position on the deck."
            }
        },
        "required": ["deck", "position"]
    }
}

_machine_set_values_schema = {
    "type": "function",
    "name": "machine_set_values",
    "description": "Set the values of the machine." + \
                    "Deck and position names are used to identify the machine's state. " +
                    "Both are numbers. Be sure to use the digit representation of the number, not the string. " + \
                    "For example, if the user provided 10, use 10, not ten." + \
                    "The machine can have multiple decks, each with multiple positions. " + \
                    "Each position has a setpoint and a temperature reading." + \
                    "Before running this tool, make sure to repeat the collected setpoint parameter. Ask the user to confirm the action, then proceed with the execution of the API",
    "parameters": {
        "type": "object",
        "properties": {
            "deck": {
                "type": "string",
                "description": "The name of the deck."
            },
            "position": {
                "type": "string",
                "description": "The name of the position on the deck."
            },
            "setpoint": {
                "type": "string",
                "description": "The setpoint temperature for the position. The setpoint is the target temperature that the machine is trying to maintain."
            }
        },
        "required": ["deck", "position", "setpoint"]
    }
}

async def _machine_get_status(args: Any) -> ToolResult:
    """
    Check the status of the machine.
    """
    if (args.get(param_deck) is None) or (args.get(param_position) is None):
        return ToolResult("No deck or position provided. Please retry", ToolResultDirection.TO_SERVER)
    
    deck_name = str(args[param_deck])
    position_name = str(args[param_position])
    if not deck_name.isdigit() or not position_name.isdigit():
        return ToolResult("Deck and position names must be numeric. Please retry with valid numbers.", ToolResultDirection.TO_SERVER)

    # Locate deck and position
    deck: Deck | None = next(
        (d for d in current_junior_state.decks if d.name == deck_name), None
    )
    if deck is None:
        return ToolResult(f"Deck {deck_name} not found.", ToolResultDirection.TO_SERVER)

    pos: PositionReading | None = next(
        (p for p in deck.positions if p.name == position_name), None
    )
    if pos is None:
        return ToolResult(f"Position {position_name} not found on deck {deck_name}.", ToolResultDirection.TO_SERVER)

    # Compose response
    parts: list[str] = []
    if pos.setpoint is not None:
        parts.append(f"Setpoint is {pos.setpoint} °C")
    if pos.temperature is not None:
        parts.append(f"Current temperature is {pos.temperature} °C")

    result_text = (f"Position {position_name} on deck {deck_name}: " + " and ".join(parts) + ".")
    return ToolResult(result_text, ToolResultDirection.TO_SERVER)

async def _machine_set_values(args: Any) -> ToolResult:
    """
    Update set-point and / or temperature for a given deck / position.
    The caller may supply either or both of the parameters “setpoint” and “temperature”.
    """
    if (args.get(param_deck) is None) or (args.get(param_position) is None):
        return ToolResult("No deck or position provided. Please retry.", ToolResultDirection.TO_SERVER)

    deck_name = str(args[param_deck])
    position_name = str(args[param_position])

    if not deck_name.isdigit() or not position_name.isdigit():
        return ToolResult(
            "Deck and position names must be numeric. Please retry with valid numbers.",
            ToolResultDirection.TO_SERVER,
        )

    # Locate deck and position
    deck: Deck | None = next(
        (d for d in current_junior_state.decks if d.name == deck_name), None
    )
    if deck is None:
        return ToolResult(f"Deck {deck_name} not found.", ToolResultDirection.TO_SERVER)

    pos: PositionReading | None = next(
        (p for p in deck.positions if p.name == position_name), None
    )
    if pos is None:
        return ToolResult(
            f"Position {position_name} not found on deck {deck_name}.",
            ToolResultDirection.TO_SERVER,
        )

    # Validate and apply new setpoint
    if param_setpoint not in args:
        return ToolResult("No setpoint provided to update.", ToolResultDirection.TO_SERVER)

    try:
        new_setpoint = float(args[param_setpoint])
    except ValueError:
        return ToolResult("Invalid setpoint value; must be a number.", ToolResultDirection.TO_SERVER)

    pos.setpoint = new_setpoint
    result_text = f"Updated position {position_name} on deck {deck_name}: new setpoint is {new_setpoint} °C."
    return ToolResult(result_text, ToolResultDirection.TO_SERVER)

def attach_machine_tools(rtmt: RTMiddleTier) -> None:
    rtmt.tools["machine_get_status"] = Tool(
        schema=_machine_get_status_schema, target=lambda args: _machine_get_status(args)
    )
    rtmt.tools["machine_set_values"] = Tool(
        schema=_machine_set_values_schema, target=lambda args: _machine_set_values(args)
    )