# Scripts Documentation

This directory contains command-line tools for working with the Expressions Tool.

## Prerequisites

Before running these scripts, you must have the live2d-py package built and installed. See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for build instructions.

Quick installation (if you have network access):
```bash
pip install live2d-py
```

Or build from source:
```bash
python setup.py build
python setup.py install
```

## Scripts Overview

### 1. `list_params.py`

Lists all parameters available in a Live2D model.

**Usage:**
```bash
python scripts/list_params.py --model Resources/v3/Haru/Haru.model3.json
```

**Output:**
```
Total parameters: 38

ID                             Type       Value      Min        Max        Default   
------------------------------------------------------------------------------------------
ParamAngleX                    Normal     0.000      -30.000    30.000     0.000     
ParamAngleY                    Normal     0.000      -30.000    30.000     0.000     
ParamAngleZ                    Normal     0.000      -30.000    30.000     0.000     
...
```

**No OpenGL required** - This script only loads the model data, not the renderer.

---

### 2. `set_expression.py`

Sets a specific expression on a Live2D model and displays it.

**Usage:**
```bash
# List available expressions
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --list

# Set a specific expression
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --expression F01

# Set expression and display for 10 seconds
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --expression F01 --duration 10
```

**Requires:**
- OpenGL context (headless servers may need virtual display)
- pygame
- Built live2d-py package

---

### 3. `play_motion.py`

Plays a specific motion from a Live2D model.

**Usage:**
```bash
# List available motion groups
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --list

# Play a specific motion
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --group Idle --index 0

# Play with custom priority and duration
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --group TapBody --index 0 --priority 2 --duration 15
```

**Motion Priorities:**
- 0 = idle (can be interrupted)
- 1 = normal
- 2 = force (interrupts lower priority)
- 3 = always force

**Requires:**
- OpenGL context
- pygame
- Built live2d-py package

---

### 4. `run_expression_lab.py`

Interactive demonstration of the Expressions Tool with keyboard controls.

**Usage:**
```bash
python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json
```

**Keyboard Controls:**

| Key | Action |
|-----|--------|
| 1 | Set expression: idle |
| 2 | Set expression: listening |
| 3 | Set expression: thinking |
| 4 | Set expression: happy |
| 5 | Set expression: confused |
| 6 | Set expression: annoyed |
| Q | Play motion: nod (TapHead group) |
| W | Play motion: shake (TapBody group) |
| E | Play motion: wave (Idle group) |
| R | Random expression |
| T | Random motion |
| ESC | Exit |

**Features:**
- Real-time FPS counter in window title
- Command queue size display
- Verbose logging of all commands
- Demonstrates thread-safe command queuing
- Shows single-writer pattern in action

**Requires:**
- OpenGL context
- pygame
- Built live2d-py package

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'live2d.v3.live2d'"

The live2d-py package hasn't been built yet. You need to:
1. Download Cubism SDK from https://www.live2d.com/sdk/download/native/
2. Build the package using CMake (see CONTRIBUTING.md)
3. Or install a pre-built wheel from releases

### "Error: Model file not found"

Make sure you provide the full path to a `.model3.json` file. Example models are in the `Resources/v3/` directory.

### OpenGL errors on headless servers

If running on a server without a display:
```bash
# Install virtual display
sudo apt-get install xvfb

# Run with virtual display
xvfb-run -a python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json
```

### Scripts won't run: "Permission denied"

Make scripts executable:
```bash
chmod +x scripts/*.py
```

---

## Integration Example

Here's how to integrate the Expressions Tool into your own application:

```python
import sys
sys.path.insert(0, 'tools')
sys.path.insert(0, 'package')

import live2d.v3 as live2d
from tools.expressions_tool import ExpressionsTool, ExpressionsRuntime

# Initialize Live2D
live2d.init()
live2d.glInit()

# Create model
model = live2d.Model()
model.LoadModelJson("path/to/model3.json")
model.CreateRenderer(2)

# Create expressions tool
tool = ExpressionsTool()
runtime = ExpressionsRuntime(tool, model, verbose=True)

# From any thread, queue commands:
tool.set_expression("happy")
tool.play_motion("TapBody", index=0, priority=2)
tool.set_param("ParamAngleX", 10.0, op="add")

# In your render loop (main thread only):
while running:
    # ... handle events ...
    
    # Process queued commands (MUST be main thread)
    runtime.update(delta_seconds)
    
    # Update model
    model.LoadParameters()
    model.UpdateMotion(delta_seconds)
    model.SaveParameters()
    model.UpdateBlink(delta_seconds)
    model.UpdateExpression(delta_seconds)
    model.UpdateDrag(delta_seconds)
    model.UpdateBreath(delta_seconds)
    model.UpdatePhysics(delta_seconds)
    model.UpdatePose(delta_seconds)
    
    # Draw
    live2d.clearBuffer()
    model.Draw()
    # ... swap buffers ...
```

---

## Testing

To verify the Expressions Tool without Live2D bindings:

```bash
# Test the tool API (no Live2D required)
python3 << 'EOF'
import sys
sys.path.insert(0, 'tools')

from expressions_tool import ExpressionsTool, CommandType, ParamOp

tool = ExpressionsTool()
tool.set_expression("happy", fade_ms=500)
tool.play_motion("TapBody", index=0, priority=2)
tool.set_param("ParamAngleX", 10.0, op="add")

assert tool.queue_size() == 3
print("✓ All API tests passed!")
EOF
```

---

## See Also

- [tool.md](../tool.md) - Complete Expressions Tool documentation
- [examples/](../examples/) - Live2D example programs
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Build and development guide
