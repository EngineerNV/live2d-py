#!/usr/bin/env python3
"""
Expression Lab - Interactive Live2D Expressions Tool Demo

A live demo that integrates the ExpressionsTool with a pygame render loop.
Demonstrates the single-writer pattern with keybindings to trigger expressions and motions.

Keybindings:
    1-6: Trigger expressions (idle, listening, thinking, happy, confused, annoyed)
    Q/W/E: Trigger motions (nod, shake, wave)
    R: Random expression
    T: Random motion
    ESC: Exit

Usage:
    python scripts/run_expression_lab.py --model path/to/model3.json
    python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json
"""

import argparse
import os
import sys
import time

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "package"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE

import live2d.v3 as live2d

# Import our expressions tool
from tools.expressions_tool import ExpressionsTool, ExpressionsRuntime


# Expression mappings for keys 1-6
EXPRESSION_MAP = {
    pygame.K_1: "idle",
    pygame.K_2: "listening", 
    pygame.K_3: "thinking",
    pygame.K_4: "happy",
    pygame.K_5: "confused",
    pygame.K_6: "annoyed",
}

# Motion mappings for keys Q/W/E
MOTION_MAP = {
    pygame.K_q: ("nod", "TapHead"),     # nod -> try TapHead group
    pygame.K_w: ("shake", "TapBody"),   # shake -> try TapBody group
    pygame.K_e: ("wave", "Idle"),       # wave -> try Idle group
}


def print_help():
    """Print keybinding help."""
    print("\n" + "=" * 60)
    print("Expression Lab - Interactive Demo")
    print("=" * 60)
    print("\nExpressions (keys 1-6):")
    for key, expr in EXPRESSION_MAP.items():
        key_name = pygame.key.name(key)
        print(f"  {key_name}: {expr}")
    
    print("\nMotions (keys Q/W/E):")
    for key, (name, fallback) in MOTION_MAP.items():
        key_name = pygame.key.name(key).upper()
        print(f"  {key_name}: {name} (fallback: {fallback})")
    
    print("\nOther keys:")
    print("  R: Random expression")
    print("  T: Random motion")
    print("  ESC: Exit")
    print("=" * 60 + "\n")


def run_expression_lab(model_path: str) -> None:
    """
    Run the interactive expression lab.
    
    Args:
        model_path: Path to model3.json file
    """
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        sys.exit(1)
    
    print(f"Loading model: {model_path}")
    
    # Initialize
    pygame.init()
    live2d.init()
    
    display = (600, 700)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Expression Lab")
    
    live2d.glInit()
    
    # Load model
    model = live2d.Model()
    model.LoadModelJson(model_path)
    model.CreateRenderer(2)
    model.Resize(*display)
    
    # Create expressions tool and runtime
    tool = ExpressionsTool(max_queue_size=100)
    runtime = ExpressionsRuntime(tool, model, verbose=True)
    
    # Print available expressions and motions
    print("\nModel loaded successfully!")
    print("\nAvailable expressions:")
    expressions = runtime.get_available_expressions()
    if expressions:
        for expr in expressions:
            print(f"  - {expr}")
    else:
        print("  (None found)")
    
    print("\nAvailable motion groups:")
    motions = runtime.get_available_motions()
    if motions:
        for group, count in motions.items():
            print(f"  - {group}: {count} motion(s)")
    else:
        print("  (None found)")
    
    print_help()
    
    # Main loop
    last_update = time.time()
    running = True
    frame_count = 0
    fps_timer = time.time()
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                break
            
            elif event.type == KEYDOWN:
                # ESC to exit
                if event.key == K_ESCAPE:
                    running = False
                    break
                
                # Expression keys (1-6)
                elif event.key in EXPRESSION_MAP:
                    expr_name = EXPRESSION_MAP[event.key]
                    print(f"\n[Keybind] Triggering expression: {expr_name}")
                    tool.set_expression(expr_name)
                
                # Motion keys (Q/W/E)
                elif event.key in MOTION_MAP:
                    motion_name, fallback_group = MOTION_MAP[event.key]
                    print(f"\n[Keybind] Triggering motion: {motion_name} (group: {fallback_group})")
                    tool.play_motion(fallback_group, index=0, priority=2)
                
                # Random expression (R)
                elif event.key == pygame.K_r:
                    print("\n[Keybind] Triggering random expression")
                    if expressions:
                        import random
                        expr = random.choice(expressions)
                        tool.set_expression(expr)
                    else:
                        print("  No expressions available")
                
                # Random motion (T)
                elif event.key == pygame.K_t:
                    print("\n[Keybind] Triggering random motion")
                    if motions:
                        import random
                        group = random.choice(list(motions.keys()))
                        tool.play_motion(group, index=-1, priority=2)
                    else:
                        print("  No motions available")
        
        if not running:
            break
        
        # Calculate delta time
        current_time = time.time()
        delta_secs = current_time - last_update
        last_update = current_time
        
        # Process commands from queue (SINGLE-WRITER: main thread only)
        commands_processed = runtime.update(delta_secs)
        
        # Update model (simplified update cycle)
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
        
        # FPS counter
        frame_count += 1
        if current_time - fps_timer >= 1.0:
            fps = frame_count / (current_time - fps_timer)
            pygame.display.set_caption(f"Expression Lab - FPS: {fps:.1f} - Queue: {tool.queue_size()}")
            frame_count = 0
            fps_timer = current_time
        
        pygame.time.wait(16)  # ~60 FPS target
    
    print("\nShutting down...")
    
    # Cleanup
    live2d.dispose()
    pygame.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Interactive Expression Lab for Live2D models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Keybindings:
  1-6: Trigger expressions (idle, listening, thinking, happy, confused, annoyed)
  Q/W/E: Trigger motions (nod, shake, wave)
  R: Random expression
  T: Random motion
  ESC: Exit

Example:
  python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json
        """
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Path to model3.json file"
    )
    
    args = parser.parse_args()
    run_expression_lab(args.model)


if __name__ == "__main__":
    main()
