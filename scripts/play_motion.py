#!/usr/bin/env python3
"""
Play Live2D Motion

Simple CLI tool to play a Live2D model motion.
Opens a window and plays the specified motion.

Usage:
    python scripts/play_motion.py --model path/to/model3.json --group TapBody --index 0
    python scripts/play_motion.py --model path/to/model3.json --list
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


def list_motions(model_path: str) -> None:
    """List available motion groups for the model."""
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        sys.exit(1)
    
    live2d.init()
    model = live2d.Model()
    model.LoadModelJson(model_path)
    
    motions = model.GetMotions()
    
    print(f"Available motion groups for {os.path.basename(model_path)}:")
    if motions:
        for group, count in motions.items():
            print(f"  - {group}: {count} motion(s)")
    else:
        print("  (No motions found)")
    
    live2d.dispose()


def play_motion(
    model_path: str, 
    group: str, 
    index: int = 0, 
    priority: int = 2,
    duration: int = 10
) -> None:
    """
    Load model, play motion, and display for specified duration.
    
    Args:
        model_path: Path to model3.json
        group: Motion group name
        index: Motion index within group
        priority: Motion priority (0-3)
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
    pygame.display.set_caption(f"Motion: {group}[{index}]")
    
    live2d.glInit()
    
    # Load model
    model = live2d.Model()
    model.LoadModelJson(model_path)
    model.CreateRenderer(2)
    model.Resize(*display)
    
    # Start the motion
    motion_started = [False]
    
    def on_start(g: str, n: int):
        print(f"Motion started: {g}[{n}]")
        motion_started[0] = True
    
    def on_finish(g: str, n: int):
        print(f"Motion finished: {g}[{n}]")
    
    print(f"Starting motion: {group}[{index}] with priority {priority}")
    
    try:
        model.StartMotion(
            group, 
            index, 
            priority,
            onStart=on_start,
            onFinish=on_finish
        )
    except Exception as e:
        print(f"Error starting motion: {e}")
        print("\nAvailable motion groups:")
        for g, count in model.GetMotions().items():
            print(f"  - {g}: {count} motion(s)")
        live2d.dispose()
        pygame.quit()
        sys.exit(1)
    
    # Display for duration
    start_time = time.time()
    last_update = start_time
    running = True
    
    print(f"Displaying for up to {duration} seconds (close window to exit early)...")
    
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
        model.UpdateBlink(delta_secs)
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
        description="Play a Live2D model motion"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Path to model3.json file"
    )
    parser.add_argument(
        "--group",
        help="Motion group name (e.g., 'Idle', 'TapBody')"
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Motion index within group (default: 0)"
    )
    parser.add_argument(
        "--priority",
        type=int,
        default=2,
        help="Motion priority 0-3 (default: 2)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="How long to display in seconds (default: 10)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available motion groups and exit"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_motions(args.model)
    elif args.group:
        play_motion(args.model, args.group, args.index, args.priority, args.duration)
    else:
        parser.print_help()
        print("\nError: Either --group or --list must be specified")
        sys.exit(1)


if __name__ == "__main__":
    main()
