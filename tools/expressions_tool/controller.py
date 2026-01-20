"""
Controller for the Expressions Tool.

Provides the public API for queueing expression, motion, and parameter commands.
Thread-safe - can be called from any thread.
"""

import queue
import threading
from typing import Optional

from .protocol import (
    Command,
    CommandType,
    ParamOp,
    SetExpressionCommand,
    PlayMotionCommand,
    SetParamCommand,
)


class ExpressionsTool:
    """
    Thread-safe API for controlling Live2D model expressions, motions, and parameters.
    
    Commands are queued and processed by ExpressionsRuntime on the main render thread.
    """
    
    def __init__(self, max_queue_size: int = 100):
        """
        Initialize the expressions tool.
        
        Args:
            max_queue_size: Maximum number of queued commands (0 = unlimited)
        """
        self._queue: queue.Queue[Command] = queue.Queue(maxsize=max_queue_size)
        self._lock = threading.Lock()
        
    def set_expression(self, name: str, fade_ms: int = 250) -> None:
        """
        Queue a command to set a Live2D expression.
        
        Args:
            name: Expression name (e.g., "happy", "sad", "angry")
            fade_ms: Fade-in duration in milliseconds
            
        Thread-safe: Can be called from any thread.
        """
        cmd: SetExpressionCommand = {
            "type": CommandType.SET_EXPRESSION,
            "name": name,
            "fade_ms": fade_ms,
        }
        with self._lock:
            try:
                self._queue.put_nowait(cmd)
            except queue.Full:
                # Drop oldest command to make room
                try:
                    self._queue.get_nowait()
                    self._queue.put_nowait(cmd)
                except queue.Empty:
                    pass
    
    def play_motion(
        self, 
        group: str, 
        index: int = 0, 
        priority: int = 1
    ) -> None:
        """
        Queue a command to play a Live2D motion.
        
        Args:
            group: Motion group name (e.g., "Idle", "TapBody")
            index: Motion index within the group (0-based, -1 for random)
            priority: Motion priority:
                0 = idle (can be interrupted)
                1 = normal
                2 = force (interrupts lower priority)
                3 = always force (always interrupts)
                
        Thread-safe: Can be called from any thread.
        """
        cmd: PlayMotionCommand = {
            "type": CommandType.PLAY_MOTION,
            "group": group,
            "index": index,
            "priority": priority,
        }
        with self._lock:
            try:
                self._queue.put_nowait(cmd)
            except queue.Full:
                # Drop oldest command to make room
                try:
                    self._queue.get_nowait()
                    self._queue.put_nowait(cmd)
                except queue.Empty:
                    pass
    
    def set_param(
        self, 
        param_id: str, 
        value: float, 
        op: str = "override"
    ) -> None:
        """
        Queue a command to set a model parameter.
        
        Args:
            param_id: Parameter ID (e.g., "ParamAngleX", "ParamEyeLOpen")
            value: Target value
            op: Operation type - "override", "add", or "multiply"
            
        Thread-safe: Can be called from any thread.
        """
        # Convert string op to ParamOp enum
        op_enum = ParamOp.OVERRIDE
        if op == "add":
            op_enum = ParamOp.ADD
        elif op == "multiply":
            op_enum = ParamOp.MULTIPLY
            
        cmd: SetParamCommand = {
            "type": CommandType.SET_PARAM,
            "param_id": param_id,
            "value": value,
            "op": op_enum,
        }
        with self._lock:
            try:
                self._queue.put_nowait(cmd)
            except queue.Full:
                # Drop oldest command to make room
                try:
                    self._queue.get_nowait()
                    self._queue.put_nowait(cmd)
                except queue.Empty:
                    pass
    
    def get_queue(self) -> queue.Queue[Command]:
        """
        Get the command queue for the runtime to consume.
        
        Returns:
            The command queue
            
        Note: Only ExpressionsRuntime should call this.
        """
        return self._queue
    
    def queue_size(self) -> int:
        """
        Get the current number of queued commands.
        
        Returns:
            Number of commands in the queue
        """
        return self._queue.qsize()
