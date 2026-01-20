#!/usr/bin/env python3
"""
Set Live2D Expression

Simple CLI tool to set a Live2D model's expression.
Opens a window and applies the specified expression.

Usage:
    python scripts/set_expression.py --model path/to/model3.json --expression happy
    python scripts/set_expression.py --model path/to/model3.json --list
"""

import argparse
import os
import sys
import time

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "package"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT

import live2d.v3 as live2d


def list_expressions(model_path: str) -> None:
    """List available expressions for the model."""
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        sys.exit(1)
    
    live2d.init()
    model = live2d.Model()
    model.LoadModelJson(model_path)
    
    expressions = model.GetExpressions()
    
    print(f"Available expressions for {os.path.basename(model_path)}:")
    if expressions:
        for expr in expressions:
            print(f"  - {expr}")
    else:
        print("  (No expressions found)")
    
    live2d.dispose()


def set_expression(model_path: str, expression_name: str, duration: int = 5) -> None:
    """
    Load model, set expression, and display for specified duration.
    
    Args:
        model_path: Path to model3.json
        expression_name: Name of expression to set
        duration: How long to display in seconds
    """
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        sys.exit(1)
    
    # Initialize
    pygame.init()
    live2d.init()
    
    display = (500, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"Expression: {expression_name}")
    
    live2d.glInit()
    
    # Load model
    model = live2d.Model()
    model.LoadModelJson(model_path)
    model.CreateRenderer(2)
    model.Resize(*display)
    
    # Set the expression
    print(f"Setting expression: {expression_name}")
    result = model.SetExpression(expression_name)
    
    if result == -1:
        print(f"Warning: Expression '{expression_name}' not found")
        print("Available expressions:")
        for expr in model.GetExpressions():
            print(f"  - {expr}")
    else:
        print(f"Expression set successfully (index: {result})")
    
    # Display for duration
    start_time = time.time()
    last_update = start_time
    running = True
    
    print(f"Displaying for {duration} seconds (close window to exit early)...")
    
    while running and (time.time() - start_time) < duration:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                break
        
        # Update model
        current_time = time.time()
        delta_secs = current_time - last_update
        last_update = current_time
        
        # Update cycle (simplified from examples/main_pygame_fine_grained.py)
        model.LoadParameters()
        model.UpdateMotion(delta_secs)
        model.SaveParameters()
        model.UpdateExpression(delta_secs)
        model.UpdateDrag(delta_secs)
        model.UpdateBreath(delta_secs)
        model.UpdatePhysics(delta_secs)
        model.UpdatePose(delta_secs)
        
        # Draw
        live2d.clearBuffer()
        model.Draw()
        pygame.display.flip()
        
        pygame.time.wait(16)  # ~60 FPS
    
    print("Done")
    
    # Cleanup
    live2d.dispose()
    pygame.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Set a Live2D model expression"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Path to model3.json file"
    )
    parser.add_argument(
        "--expression",
        help="Expression name to set"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="How long to display in seconds (default: 5)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available expressions and exit"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_expressions(args.model)
    elif args.expression:
        set_expression(args.model, args.expression, args.duration)
    else:
        parser.print_help()
        print("\nError: Either --expression or --list must be specified")
        sys.exit(1)


if __name__ == "__main__":
    main()
