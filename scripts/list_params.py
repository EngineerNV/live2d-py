#!/usr/bin/env python3
"""
List Live2D Model Parameters

Displays all available parameters for a given Live2D model, including:
- Parameter ID
- Type
- Current value
- Min/Max range
- Default value

Usage:
    python scripts/list_params.py --model path/to/model3.json
"""

import argparse
import os
import sys

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "package"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import live2d.v3 as live2d


def list_parameters(model_path: str) -> None:
    """
    Load a model and print all its parameters.
    
    Args:
        model_path: Path to model3.json file
    """
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        sys.exit(1)
    
    # Initialize Live2D
    live2d.init()
    
    print(f"Loading model: {model_path}")
    print()
    
    # Load model (no OpenGL context needed for parameter listing)
    model = live2d.Model()
    model.LoadModelJson(model_path)
    
    # Get parameter count
    param_count = model.GetParameterCount()
    print(f"Total parameters: {param_count}")
    print()
    
    # Print header
    print(f"{'ID':<30} {'Type':<10} {'Value':<10} {'Min':<10} {'Max':<10} {'Default':<10}")
    print("-" * 90)
    
    # List all parameters
    for i in range(param_count):
        param = model.GetParameter(i)
        print(f"{param.id:<30} {param.type:<10} {param.value:<10.3f} {param.min:<10.3f} {param.max:<10.3f} {param.default:<10.3f}")
    
    print()
    print(f"Listed {param_count} parameters")
    
    # Clean up
    live2d.dispose()


def main():
    parser = argparse.ArgumentParser(
        description="List all parameters for a Live2D model"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Path to model3.json file"
    )
    
    args = parser.parse_args()
    list_parameters(args.model)


if __name__ == "__main__":
    main()
