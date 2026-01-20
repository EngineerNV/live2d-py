#!/usr/bin/env python3
"""
Test script to validate the Expressions Tool package.

This test doesn't require the Live2D bindings to be built.
It validates:
- No circular imports
- API correctness
- Queue operations
- Command protocol
"""

import sys
import os

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_imports():
    """Test that all modules can be imported without circular dependencies."""
    print("Testing imports...")
    
    from tools.expressions_tool import ExpressionsTool, ExpressionsRuntime
    from tools.expressions_tool import CommandType, ParamOp
    from tools.expressions_tool.protocol import (
        SetExpressionCommand,
        PlayMotionCommand, 
        SetParamCommand
    )
    
    print("  ✓ All imports successful")


def test_api():
    """Test the ExpressionsTool API."""
    print("\nTesting API...")
    
    from tools.expressions_tool import ExpressionsTool, CommandType, ParamOp
    
    tool = ExpressionsTool(max_queue_size=10)
    
    # Test set_expression
    tool.set_expression("happy", fade_ms=500)
    assert tool.queue_size() == 1
    print("  ✓ set_expression() works")
    
    # Test play_motion
    tool.play_motion("TapBody", index=0, priority=2)
    assert tool.queue_size() == 2
    print("  ✓ play_motion() works")
    
    # Test set_param with all operations
    tool.set_param("ParamAngleX", 10.0, op="override")
    tool.set_param("ParamAngleY", 5.0, op="add")
    tool.set_param("ParamAngleZ", 2.0, op="multiply")
    assert tool.queue_size() == 5
    print("  ✓ set_param() works with all operations")


def test_queue_operations():
    """Test queue operations and command format."""
    print("\nTesting queue operations...")
    
    from tools.expressions_tool import ExpressionsTool, CommandType, ParamOp
    
    tool = ExpressionsTool()
    
    # Queue commands
    tool.set_expression("happy", fade_ms=250)
    tool.play_motion("Idle", index=-1, priority=1)
    tool.set_param("ParamEyeLOpen", 1.0, op="override")
    
    queue = tool.get_queue()
    
    # Verify first command (expression)
    cmd = queue.get_nowait()
    assert cmd["type"] == CommandType.SET_EXPRESSION
    assert cmd["name"] == "happy"
    assert cmd["fade_ms"] == 250
    print("  ✓ Expression command format correct")
    
    # Verify second command (motion)
    cmd = queue.get_nowait()
    assert cmd["type"] == CommandType.PLAY_MOTION
    assert cmd["group"] == "Idle"
    assert cmd["index"] == -1
    assert cmd["priority"] == 1
    print("  ✓ Motion command format correct")
    
    # Verify third command (param)
    cmd = queue.get_nowait()
    assert cmd["type"] == CommandType.SET_PARAM
    assert cmd["param_id"] == "ParamEyeLOpen"
    assert cmd["value"] == 1.0
    assert cmd["op"] == ParamOp.OVERRIDE
    print("  ✓ Parameter command format correct")


def test_thread_safety():
    """Test thread-safe operations."""
    print("\nTesting thread safety...")
    
    import threading
    from tools.expressions_tool import ExpressionsTool
    
    tool = ExpressionsTool()
    
    def worker():
        for i in range(10):
            tool.set_expression(f"expr_{i}")
            tool.play_motion(f"group_{i}", index=i)
            tool.set_param(f"param_{i}", float(i))
    
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Should have 5 threads * 10 iterations * 3 commands = 150 commands
    # (or less if queue overflow occurred)
    size = tool.queue_size()
    assert size > 0
    print(f"  ✓ Thread-safe operations work (queued {size} commands from 5 threads)")


def test_queue_overflow():
    """Test queue overflow handling."""
    print("\nTesting queue overflow...")
    
    from tools.expressions_tool import ExpressionsTool
    
    tool = ExpressionsTool(max_queue_size=5)
    
    # Fill queue beyond capacity
    for i in range(10):
        tool.set_expression(f"expr_{i}")
    
    # Should have at most 5 commands (with oldest dropped)
    size = tool.queue_size()
    assert size <= 5
    print(f"  ✓ Queue overflow handled correctly (size: {size})")


def test_runtime_mock():
    """Test runtime with a mock model."""
    print("\nTesting runtime with mock model...")
    
    from tools.expressions_tool import ExpressionsTool, ExpressionsRuntime
    
    # Create mock model
    class MockModel:
        def SetExpression(self, name):
            return 0
        
        def StartMotion(self, group, index, priority):
            pass
        
        def SetParameterValue(self, param_id, value, weight):
            pass
        
        def GetParameterValue(self, param_id):
            return 0.0
        
        def GetExpressions(self):
            return ["happy", "sad", "angry"]
        
        def GetMotions(self):
            return {"Idle": 3, "TapBody": 5}
    
    tool = ExpressionsTool()
    model = MockModel()
    runtime = ExpressionsRuntime(tool, model, verbose=False)
    
    # Queue some commands
    tool.set_expression("happy")
    tool.play_motion("Idle", index=0, priority=2)
    tool.set_param("ParamAngleX", 10.0, op="add")
    
    # Process commands
    processed = runtime.update(0.016)
    assert processed == 3
    assert tool.queue_size() == 0
    
    print(f"  ✓ Runtime processed {processed} commands correctly")
    
    # Test info methods
    expressions = runtime.get_available_expressions()
    assert len(expressions) == 3
    print(f"  ✓ get_available_expressions() works: {expressions}")
    
    motions = runtime.get_available_motions()
    assert len(motions) == 2
    print(f"  ✓ get_available_motions() works: {motions}")


def main():
    print("=" * 60)
    print("Expressions Tool - Validation Tests")
    print("=" * 60)
    
    try:
        test_imports()
        test_api()
        test_queue_operations()
        test_thread_safety()
        test_queue_overflow()
        test_runtime_mock()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe Expressions Tool package is working correctly!")
        print("No circular imports detected.")
        print("Ready for integration with Live2D models.")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
