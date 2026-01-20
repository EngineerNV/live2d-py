"""
Expressions Tool for Live2D Models

A thread-safe API for controlling Live2D expressions, motions, and parameters
from external agents. Uses a command queue pattern to ensure all model updates
happen on the main render thread.

Usage:
    from tools.expressions_tool import ExpressionsTool, ExpressionsRuntime
    
    # Create the tool and runtime
    tool = ExpressionsTool()
    runtime = ExpressionsRuntime(tool, model)
    
    # From any thread:
    tool.set_expression("happy")
    tool.play_motion("TapBody", index=0, priority=2)
    tool.set_param("ParamAngleX", 10.0, op="add")
    
    # In your render loop (main thread only):
    runtime.update(delta_seconds)
"""

from .controller import ExpressionsTool
from .runtime import ExpressionsRuntime
from .protocol import CommandType, ParamOp

__all__ = ["ExpressionsTool", "ExpressionsRuntime", "CommandType", "ParamOp"]
