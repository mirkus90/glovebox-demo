from pydantic import BaseModel, Field

class PositionReading(BaseModel):
    """Temperature info for a single location on the deck."""
    name: str = Field(..., description="Human-readable position identifier")
    setpoint: float = Field(..., description="Target temperature (°C)")
    temperature: float = Field(..., description="Measured temperature (°C)")


class Deck(BaseModel):
    """Identify a deck and temperature readings for its positions."""
    name: str = Field(..., description="Human-readable deck identifier")
    positions: list[PositionReading] = Field(
        ..., min_items=1, description="Array of position readings on that deck"
    )

class JuniorMachineState(BaseModel):
    """State of the Junior machine."""
    decks: list[Deck] = Field(
        ..., min_items=1, description="Array of decks with their temperature readings"
    )