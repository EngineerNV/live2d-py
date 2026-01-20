"""
Runtime integration for the Expressions Tool.

Drains the command queue and applies commands to the Live2D model.
MUST be called only from the main render thread.
"""

import queue
from typing import Any, Optional

from .protocol import Command, CommandType, ParamOp
from .controller import ExpressionsTool


class ExpressionsRuntime:
    """
    Runtime integration that drains commands and applies them to a Live2D model.
    
    MUST be called only from the main render thread to maintain the single-writer guarantee.
    """
    
    def __init__(self, tool: ExpressionsTool, model: Any, verbose: bool = False):
        """
        Initialize the runtime.
        
        Args:
            tool: ExpressionsTool instance to drain commands from
            model: Live2D model instance (LAppModel or Model)
            verbose: If True, print debug logs for each command
        """
        self._tool = tool
        self._model = model
        self._verbose = verbose
        self._queue = tool.get_queue()
        
        # Cache available expressions and motions for validation
        self._available_expressions: Optional[list[str]] = None
        self._available_motions: Optional[dict[str, int]] = None
        self._param_cache: Optional[dict[str, tuple[float, float]]] = None
        
    def update(self, delta_seconds: float = 0.016) -> int:
        """
        Drain the command queue and apply commands to the model.
        
        Call this once per frame from your render loop (main thread only).
        
        Args:
            delta_seconds: Time elapsed since last frame (unused, for future extensions)
            
        Returns:
            Number of commands processed this frame
            
        MUST be called from main render thread only.
        """
        commands_processed = 0
        
        # Drain all pending commands
        while True:
            try:
                cmd = self._queue.get_nowait()
                self._apply_command(cmd)
                commands_processed += 1
            except queue.Empty:
                break
                
        return commands_processed
    
    def _apply_command(self, cmd: Command) -> None:
        """
        Apply a single command to the model.
        
        Args:
            cmd: Command to apply
        """
        cmd_type = cmd["type"]
        
        if cmd_type == CommandType.SET_EXPRESSION:
            self._apply_set_expression(cmd)
        elif cmd_type == CommandType.PLAY_MOTION:
            self._apply_play_motion(cmd)
        elif cmd_type == CommandType.SET_PARAM:
            self._apply_set_param(cmd)
        else:
            if self._verbose:
                print(f"[ExpressionsRuntime] Unknown command type: {cmd_type}")
    
    def _apply_set_expression(self, cmd: dict) -> None:
        """Apply a set_expression command."""
        name = cmd["name"]
        fade_ms = cmd.get("fade_ms", 250)
        
        if self._verbose:
            print(f"[ExpressionsRuntime] Setting expression: {name} (fade: {fade_ms}ms)")
        
        # Try to set the expression by name
        # Check if model has SetExpression method (v3 Model API)
        if hasattr(self._model, "SetExpression"):
            try:
                # For v3 Model: SetExpression(expressionId)
                # Returns: expression index or -1 if not found
                result = self._model.SetExpression(name)
                if result == -1 and self._verbose:
                    print(f"[ExpressionsRuntime] Expression '{name}' not found in model")
                return
            except Exception as e:
                if self._verbose:
                    print(f"[ExpressionsRuntime] Error setting expression: {e}")
        
        # Fallback: Try SetRandomExpression for LAppModel
        if hasattr(self._model, "SetRandomExpression"):
            try:
                self._model.SetRandomExpression()
                if self._verbose:
                    print(f"[ExpressionsRuntime] Expression '{name}' not found, using random")
            except Exception as e:
                if self._verbose:
                    print(f"[ExpressionsRuntime] Error setting random expression: {e}")
    
    def _apply_play_motion(self, cmd: dict) -> None:
        """Apply a play_motion command."""
        group = cmd["group"]
        index = cmd.get("index", 0)
        priority = cmd.get("priority", 1)
        
        if self._verbose:
            print(f"[ExpressionsRuntime] Playing motion: {group}[{index}] priority={priority}")
        
        # Try StartMotion first (v3 Model and LAppModel)
        if hasattr(self._model, "StartMotion"):
            try:
                if index == -1:
                    # Random motion in group
                    if hasattr(self._model, "StartRandomMotion"):
                        self._model.StartRandomMotion(group, priority)
                    else:
                        # Fallback: pick index 0
                        self._model.StartMotion(group, 0, priority)
                else:
                    self._model.StartMotion(group, index, priority)
                return
            except Exception as e:
                if self._verbose:
                    print(f"[ExpressionsRuntime] Error starting motion: {e}")
        
        # Fallback: Try StartRandomMotion
        if hasattr(self._model, "StartRandomMotion"):
            try:
                if group:
                    self._model.StartRandomMotion(group, priority)
                else:
                    self._model.StartRandomMotion(priority=priority)
                if self._verbose:
                    print(f"[ExpressionsRuntime] Motion '{group}[{index}]' not found, using random")
            except Exception as e:
                if self._verbose:
                    print(f"[ExpressionsRuntime] Error starting random motion: {e}")
    
    def _apply_set_param(self, cmd: dict) -> None:
        """Apply a set_param command."""
        param_id = cmd["param_id"]
        value = cmd["value"]
        op = cmd.get("op", ParamOp.OVERRIDE)
        
        if self._verbose:
            print(f"[ExpressionsRuntime] Setting param: {param_id} = {value} (op: {op.value})")
        
        if not hasattr(self._model, "SetParameterValue"):
            if self._verbose:
                print(f"[ExpressionsRuntime] Model doesn't support SetParameterValue")
            return
        
        try:
            # Get current value if needed for add/multiply
            current_value = 0.0
            if op in (ParamOp.ADD, ParamOp.MULTIPLY) and hasattr(self._model, "GetParameterValue"):
                try:
                    current_value = self._model.GetParameterValue(param_id)
                except:
                    pass
            
            # Calculate final value based on operation
            if op == ParamOp.OVERRIDE:
                final_value = value
            elif op == ParamOp.ADD:
                final_value = current_value + value
            elif op == ParamOp.MULTIPLY:
                final_value = current_value * value
            else:
                final_value = value
            
            # Apply the parameter
            # SetParameterValue(id, value, weight=1.0)
            self._model.SetParameterValue(param_id, final_value, 1.0)
            
        except Exception as e:
            if self._verbose:
                print(f"[ExpressionsRuntime] Error setting parameter '{param_id}': {e}")
    
    def get_available_expressions(self) -> list[str]:
        """
        Get list of available expressions from the model.
        
        Returns:
            List of expression names
        """
        if self._available_expressions is None:
            self._available_expressions = []
            if hasattr(self._model, "GetExpressions"):
                try:
                    self._available_expressions = self._model.GetExpressions()
                except:
                    pass
        return self._available_expressions
    
    def get_available_motions(self) -> dict[str, int]:
        """
        Get available motion groups from the model.
        
        Returns:
            Dictionary mapping group names to motion counts
        """
        if self._available_motions is None:
            self._available_motions = {}
            if hasattr(self._model, "GetMotions"):
                try:
                    motions = self._model.GetMotions()
                    # motions is typically a dict like {"Idle": 3, "TapBody": 5}
                    self._available_motions = motions
                except:
                    pass
        return self._available_motions
