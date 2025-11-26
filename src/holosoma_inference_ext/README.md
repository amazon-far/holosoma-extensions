# Holosoma Inference Extension

Extension package for Holosoma Inference that adds support for the Unitree Go2 quadruped robot.

## Installation

**Option 1: Use automated setup script (Recommended)**

```bash
# One-time setup: creates conda environment 'hsinference' and installs package
bash scripts/setup_inference.sh
```

**Option 2: Manual installation**

```bash
cd src/holosoma_inference_ext
pip install -e .
```

See [scripts/README.md](../../scripts/README.md) for more details on setup scripts.

## Configuration Files

This package provides:
- Robot configuration: `holosoma_inference_ext.config_values.robot.go2_12dof`
- Observation configuration: `holosoma_inference_ext.config_values.observation.loco_go2_12dof`
- Robot models: `data/robots/go2/` (URDF and MuJoCo XML)

## Usage

The configurations are automatically registered with holosoma_inference when this package is installed.

### Gait Configuration

The Go2 policy supports two quadruped gait patterns that can be configured via the `phase_type` parameter:

- **Trot** (default): Diagonal pairs move together (FL+RR, FR+RL)
  - Phase pattern: `[0, π, π, 0]` for `[FL, FR, RL, RR]`
  - Faster, more dynamic gait

- **Walk**: Sequential leg movement
  - Phase pattern: `[0, π/2, π, 3π/2]`
  - Slower, more stable gait

```bash
# Use trot gait (default)
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path=model.onnx

# Use walk gait
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path=model.onnx \
    --task.phase-type=walk

# Adjust gait period
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path=model.onnx \
    --task.gait-period=0.8
```

### Method 1: Use the extension entry point (Recommended)

```bash
# Run with a local model
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path path/to/model.onnx

# Run with model from WandB
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path wandb://project/run/model.onnx

# Simulation mode
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path ./model.onnx \
    --task.deploy-mode sim

# Real robot deployment
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path ./model.onnx \
    --task.deploy-mode real
```

### Method 2: Use the core holosoma_inference CLI

```bash
# Extension configs are auto-registered, so this works too
python -m holosoma_inference.run_policy inference:go2-12dof-loco \
    --task.model-path path/to/model.onnx
```

### Method 3: Use Python API

```python
from holosoma_inference.policies import LocomotionPolicy
from holosoma_inference_ext.config_values.inference import go2_12dof_loco

# Use the pre-configured Go2 inference config
config = go2_12dof_loco
config.task.model_path = "path/to/model.onnx"

policy = LocomotionPolicy(config)
policy.run()
```

## Configuration Structure

### Robot Configuration (`config_values/robot.py`)

Defines the robot hardware and control parameters using pydantic dataclasses:
- **Identity**: `robot_type="go2_12dof"`, `robot="go2"`
- **Dimensions**: 12 DOF (3 per leg: hip, thigh, calf)
- **Joint names**: FL/FR/RL/RR_{hip,thigh,calf}_joint
- **Default pose**: Standing configuration
- **Joint limits**: Position, velocity, and effort limits
- **Control gains**: Can be specified or loaded from ONNX metadata
- **SDK config**: Unitree SDK, GO2 message protocol

### Observation Configuration (`config_values/observation.py`)

Defines the policy observation space:
- **Components**: `base_ang_vel`, `projected_gravity`, `command_lin_vel`, `command_ang_vel`, `dof_pos`, `dof_vel`, `actions`, `sin_phase`, `cos_phase`
- **Dimensions**: Total of 3+3+2+1+12+12+12+4+4 = 53
- **Phase observations**: 4D phase for quadruped gait (FL, FR, RL, RR)
- **Normalization scales**: Applied to each observation component
- **History**: Single timestep (no history stacking)

### Robot Models

The package includes two robot model formats:

1. **URDF** (`data/robots/go2/go2_12dof.urdf`):
   - Used for IsaacGym/IsaacSim training
   - Includes accurate inertial properties
   - DAE visual meshes

2. **MuJoCo XML** (`data/robots/go2/go2.xml`):
   - Used for MuJoCo-based inference/simulation
   - Adapted from holosoma codebase
   - Optimized contact parameters for quadruped locomotion

## Development

To extend this package:

1. Add new robot configurations in `config_values/robot.py`
2. Add corresponding observation configs in `config_values/observation.py`
3. Add robot models in `data/robots/<robot_name>/`
4. Update `DEFAULTS` dictionaries to register new configs
5. Update `setup.py` package_data if adding new file types

## Architecture

This package follows the same extension pattern as `holosoma_ext`:
- `holosoma_ext`: Extends training framework (holosoma)
- `holosoma_inference_ext`: Extends inference/deployment framework (holosoma_inference)

Both live under `src/` for consistency.

## Technical Details

### Quadruped Phase Support

The inference extension uses monkey-patching to override the base `LocomotionPolicy` class to support quadruped gaits:

1. **Phase Initialization**: Overrides `_init_phase_components()` to initialize 4-phase gait instead of 2-phase bipedal
2. **Gait Pattern Selection**: Reads `phase_type` from config to select trot or walk pattern
3. **Phase Reset**: Overrides `_handle_start_policy()` and `update_phase_time()` to use quadruped patterns

The patching happens in `__init__.py` when the package is imported:

```python
class LocomotionPolicy(_LocomotionPolicyBase):
    def _init_phase_components(self):
        phase_type = getattr(self.config.task, 'phase_type', 'trot')
        if phase_type == 'trot':
            self.phase = np.array([[0.0, π, π, 0.0]])  # FL, FR, RL, RR
        elif phase_type == 'walk':
            self.phase = np.array([[0.0, π/2, π, 3π/2]])
```

This approach allows quadruped support without modifying the core holosoma_inference codebase.

### Observation Dimensions

The Go2 configuration ensures 53-dimensional observations:
- Base angular velocity: 3D
- Projected gravity: 3D
- Linear velocity command: 2D
- Angular velocity command: 1D
- Joint positions: 12D (3 joints × 4 legs)
- Joint velocities: 12D
- Last actions: 12D
- **Sine phase: 4D** (one per leg)
- **Cosine phase: 4D** (one per leg)

This matches the training observation space defined in `holosoma_ext`.
