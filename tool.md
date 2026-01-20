# Expressions Tool

## Goal
Create a safe, thread-aware API for triggering Live2D expressions, motions, and parameter changes that can be called by external agents. The tool uses a command queue pattern to ensure all model updates happen on the main render thread.

## Non-Goals
- Speech-to-text (STT) integration
- Large language model (LLM) integration
- Text-to-speech (TTS) integration
- Audio processing beyond existing lipsync features
- Real-time facial tracking (see `examples/mediapipe_capture` for that)

## Architecture

### Single-Writer Render Loop Rule
Live2D models can only be safely modified from the OpenGL render thread. To support external control while maintaining thread safety, we use a **single-writer pattern**:

1. **External API** (`ExpressionsTool` in `controller.py`): Thread-safe methods that publish commands to a queue
2. **Command Queue**: Thread-safe FIFO queue for commands
3. **Runtime Integration** (`runtime.py`): Drains the queue and applies commands to the model **only** from the main render thread during the update loop

```
┌──────────────┐         ┌─────────┐         ┌────────────┐
│ External API │ ──cmd──>│  Queue  │ ──cmd──>│ Render Loop│
│ (any thread) │         │         │         │ (main only)│
└──────────────┘         └─────────┘         └────────────┘
```

## Tool API

### `set_expression(name: str, fade_ms: int = 250)`
Sets a Live2D expression by name.

**Parameters:**
- `name`: Expression name (e.g., "happy", "sad", "angry")
- `fade_ms`: Fade-in duration in milliseconds (default: 250)

**Behavior:**
- Replaces the current expression
- Fades smoothly between expressions
- Falls back gracefully if expression doesn't exist

### `play_motion(group: str, index: int = 0, priority: int = 1)`
Plays a motion from a motion group.

**Parameters:**
- `group`: Motion group name (e.g., "Idle", "TapBody")
- `index`: Motion index within the group (default: 0, -1 for random)
- `priority`: Motion priority (0=idle, 1=normal, 2=force, 3=always force)

**Behavior:**
- Higher priority motions can interrupt lower priority ones
- Priority 3 (force) always plays, interrupting current motion
- Falls back gracefully if group/index doesn't exist

### `set_param(param_id: str, value: float, op: str = "override")`
Sets a model parameter value.

**Parameters:**
- `param_id`: Parameter ID (e.g., "ParamAngleX", "ParamEyeLOpen")
- `value`: Target value
- `op`: Operation type - one of:
  - `"override"`: Replace the parameter value completely
  - `"add"`: Add to the current parameter value
  - `"multiply"`: Multiply the current parameter value

**Behavior:**
- Changes are applied during the next render frame
- Values are clamped to parameter min/max ranges
- Invalid parameter IDs are logged and ignored

## V1 Implementation

### Expressions (v1)
The following expressions are targeted for v1. Actual availability depends on the model:
- `idle` - Neutral/default expression
- `listening` - Attentive, focused expression
- `thinking` - Contemplative expression
- `happy` - Positive, smiling expression
- `confused` - Puzzled expression
- `annoyed` - Slightly frustrated expression

**Fallback:** If named expressions don't exist in the model, the tool will:
1. List available expressions from the model
2. Map semantic names to available expressions where possible
3. Use `SetRandomExpression()` as a fallback

### Motions (v1)
Target motion groups and actions:
- **Idle loop**: Continuous idle animation (if "Idle" group exists)
- **Gestures**:
  - `nod` - Head nod (affirmative)
  - `shake` - Head shake (negative)
  - `wave` - Hand wave (greeting)

**Fallback:** The tool will:
1. Query available motion groups from the model
2. Map semantic actions to existing groups (e.g., "TapBody", "TapHead")
3. Fall back to `StartRandomMotion()` if specific groups don't exist

## Acceptance Tests (Manual)

### Test 1: Keybind Triggers
**Procedure:**
1. Run `python scripts/run_expression_lab.py --model Resources/v3/Haru/Haru.model3.json`
2. Press keys 1-6 to trigger different expressions
3. Press keys Q, W, E to trigger motions

**Expected:**
- Each keypress triggers the corresponding expression/motion
- Debug logs show command being queued and applied
- Visual feedback shows the expression/motion change

### Test 2: Rapid Switching
**Procedure:**
1. Run expression lab
2. Rapidly press keys 1-6 in quick succession (spam for 5 seconds)
3. Rapidly press Q, W, E in quick succession

**Expected:**
- No crashes or freezes
- All commands are processed
- Model state remains valid
- No visual glitches or corruption

### Test 3: Stable FPS
**Procedure:**
1. Run expression lab with FPS counter
2. Trigger expressions and motions normally
3. Monitor FPS over 60 seconds

**Expected:**
- FPS remains stable (target: 30-60 FPS)
- No significant FPS drops during expression/motion changes
- Smooth animations throughout

### Test 4: Parameter Override
**Procedure:**
1. Use `scripts/list_params.py` to list available parameters
2. Use `set_param()` with override, add, and multiply operations
3. Verify parameter changes in the model

**Expected:**
- Parameters change as specified
- Operations work correctly (override, add, multiply)
- Invalid parameters are gracefully ignored

## Implementation Notes

### Thread Safety
- All public API methods in `ExpressionsTool` acquire locks before queue operations
- The queue itself (`queue.Queue`) is thread-safe
- Only the runtime integration modifies the model (single-writer guarantee)

### Error Handling
- Invalid expressions/motions are logged but don't crash
- Queue overflow (if implemented) will drop oldest commands
- Missing parameters are logged and ignored

### Performance
- Command queue is drained once per frame
- Batch operations are supported (multiple commands per frame)
- Minimal overhead when queue is empty

### Testing Without Agent Stack
All scripts are standalone and can run without:
- LLM inference engines
- Audio processing pipelines
- Network services
- External dependencies beyond pygame and live2d

Simply provide a model path and the scripts will work.
