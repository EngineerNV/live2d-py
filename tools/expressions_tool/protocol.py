"""
Protocol definitions for the Expressions Tool.

Defines the command format and operation types used for communication
between the external API and the render loop.
"""

from enum import Enum
from typing import TypedDict, Literal


class CommandType(Enum):
    """Types of commands that can be sent to the model."""
    SET_EXPRESSION = "set_expression"
    PLAY_MOTION = "play_motion"
    SET_PARAM = "set_param"


class ParamOp(Enum):
    """Operations for setting parameter values."""
    OVERRIDE = "override"  # Replace the parameter value
    ADD = "add"            # Add to the current value
    MULTIPLY = "multiply"  # Multiply the current value


class SetExpressionCommand(TypedDict):
    """Command to set a Live2D expression."""
    type: Literal[CommandType.SET_EXPRESSION]
    name: str
    fade_ms: int


class PlayMotionCommand(TypedDict):
    """Command to play a Live2D motion."""
    type: Literal[CommandType.PLAY_MOTION]
    group: str
    index: int
    priority: int


class SetParamCommand(TypedDict):
    """Command to set a model parameter."""
    type: Literal[CommandType.SET_PARAM]
    param_id: str
    value: float
    op: ParamOp


# Union type for all commands
Command = SetExpressionCommand | PlayMotionCommand | SetParamCommand
