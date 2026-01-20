# Terminal Commands Reference

## Prerequisites

Ensure you have the live2d-py package built and installed:
```bash
pip install live2d-py
```

Or if building from source, follow the instructions in CONTRIBUTING.md.

## Running the Scripts

### 1. List Model Parameters

Shows all available parameters in a Live2D model:

```bash
python scripts/list_params.py --model Resources/v3/Haru/Haru.model3.json
```

**Alternative models:**
```bash
python scripts/list_params.py --model Resources/v3/Mao/Mao.model3.json
python scripts/list_params.py --model Resources/v3/llny/llny.model3.json
python scripts/list_params.py --model Resources/v3/nn/nn.model3.json
```

### 2. Set Expression

List available expressions:
```bash
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --list
```

Set a specific expression:
```bash
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --expression F01
```

Set expression with custom duration (10 seconds):
```bash
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --expression F02 --duration 10
```

### 3. Play Motion

List available motion groups:
```bash
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --list
```

Play a specific motion:
```bash
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --group Idle --index 0
```

Play with custom priority and duration:
```bash
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --group TapBody --index 0 --priority 2 --duration 15
```

Play random motion from a group:
```bash
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --group TapHead --index -1
```

### 4. Expression Lab (Interactive Demo)

Main interactive demo with keyboard controls:
```bash
python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json
```

**Keyboard controls:**
- **1-6**: Set expressions (idle, listening, thinking, happy, confused, annoyed)
- **Q**: Play nod motion
- **W**: Play shake motion  
- **E**: Play wave motion
- **R**: Random expression
- **T**: Random motion
- **ESC**: Exit

**Try with different models:**
```bash
python scripts/run_expression_lab.py --model Resources/v3/Mao/Mao.model3.json
python scripts/run_expression_lab.py --model Resources/v3/llny/llny.model3.json
```

## Validation Testing

Run the validation tests (no Live2D bindings required):
```bash
python test_expressions_tool.py
```

This tests:
- Import system (no circular imports)
- API correctness
- Queue operations
- Thread safety
- Overflow handling
- Runtime integration

## On Headless Servers

If running on a server without a display, use Xvfb:

```bash
# Install Xvfb
sudo apt-get install xvfb

# Run with virtual display
xvfb-run -a python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json
```

## Using Custom Model Paths

If you have models in a different location:

```bash
python scripts/list_params.py --model /path/to/your/model.model3.json
python scripts/set_expression.py --model /path/to/your/model.model3.json --list
python scripts/play_motion.py --model /path/to/your/model.model3.json --list
python scripts/run_expression_lab.py --model /path/to/your/model.model3.json
```

## Debugging

Enable verbose output by modifying the scripts or by checking the console output. The Expression Lab automatically shows verbose logging for all commands.

To see model information:
```bash
# List parameters to see available parameter IDs
python scripts/list_params.py --model Resources/v3/Haru/Haru.model3.json

# List expressions
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --list

# List motion groups
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --list
```

## Quick Start Example

```bash
# 1. Run validation tests first
python test_expressions_tool.py

# 2. Check what's available in your model
python scripts/list_params.py --model Resources/v3/Haru/Haru.model3.json
python scripts/set_expression.py --model Resources/v3/Haru/Haru.model3.json --list
python scripts/play_motion.py --model Resources/v3/Haru/Haru.model3.json --list

# 3. Run the interactive demo
python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json
```

## Integration into Your Code

See `scripts/README.md` for full integration examples, or check the Expression Lab source code for a complete working example.

Basic integration:
```python
import sys
sys.path.insert(0, 'tools')
sys.path.insert(0, 'package')

import live2d.v3 as live2d
from tools.expressions_tool import ExpressionsTool, ExpressionsRuntime

# ... initialize Live2D and create model ...

tool = ExpressionsTool()
runtime = ExpressionsRuntime(tool, model, verbose=True)

# In render loop:
runtime.update(delta_seconds)

# From anywhere:
tool.set_expression("happy")
tool.play_motion("TapBody", index=0, priority=2)
```
