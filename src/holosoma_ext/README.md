# holosoma_ext - Go2 Quadruped Extension

`holosoma_ext` is an extension package for the `holosoma` training framework that adds support for the Unitree Go2 quadruped robot. This extension demonstrates how to add new robot types to holosoma without modifying the core framework.

## Overview

This extension provides:
- **Robot configuration** for the Unitree Go2 12-DOF quadruped
- **Quadruped-specific observations** including 4-phase gait timing
- **Locomotion rewards** tuned for quadruped gaits
- **URDF and MuJoCo XML models** for the Go2 robot
- **Custom gait manager** supporting trot and walk patterns
- **Path resolution utilities** for `@holosoma_ext/` asset references

## Quick Start

### Installation

**Option 1: Use automated setup scripts (Recommended)**

```bash
# For IsaacGym
bash scripts/setup_isaacgym.sh

# For IsaacSim
bash scripts/setup_isaacsim.sh

# For MuJoCo (inference-only)
bash scripts/setup_mujoco.sh

# For inference stack
bash scripts/setup_inference.sh

# Activate the environment
source scripts/source_isaacgym_setup.sh
source scripts/source_isaacsim_setup.sh
source scripts/source_mujoco_setup.sh
source scripts/source_inference_setup.sh
```

These scripts automatically set up the conda environment and install holosoma_ext. See [scripts/README.md](../../scripts/README.md) for details.

**Option 2: Manual installation**

```bash
cd src/holosoma_ext
pip install -e .
```

### Training

```bash
# Activate the environment (if using setup scripts)
source scripts/source_isaacgym_setup.sh

# Train Go2 locomotion policy
python -m holosoma_ext.train_agent exp:go2-12dof
```

### Sim2Sim Testing

Test trained policies in simulation before deploying to hardware:

1. Start MuJoCo environment:

```bash
source scripts/source_mujoco_setup.sh
python -m holosoma_ext.run_sim robot:go2-12dof --simulator.config.virtual-gantry.enabled False
```

2. Launch the policy (in a separate terminal):

```bash
source scripts/source_inference_setup.sh
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path=path/to/model.onnx
```

Note that we provide a pre-trained model in `src/holosoma_inference_ext/holosoma_inference_ext/models/model_go2.onnx` for testing.

### Policy Controls

Commands for controlling policies during execution:

#### General Controls

| Action | Keyboard | Joystick |
|--------|----------|----------|
| Start the policy | `]` | A button |
| Stop the policy | `o` | B button |
| Set robot to default pose | `i` | Y button |
| Kill controller program | `-` | L1 (LB) + R1 (RB) |

#### Locomotion (Velocity Tracking)

| Action | Keyboard | Joystick |
|--------|----------|----------|
| Switch walking/standing | `=` | Start button |
| Adjust linear velocity | `w` `a` `s` `d` | Left stick |
| Adjust angular velocity | `q` `e` | Right stick |

### Inference

See `holosoma_inference_ext` package for deployment capabilities. For setup:

```bash
bash scripts/setup_inference.sh  # One-time setup
source scripts/source_inference_setup.sh  # Activate environment
```

## Architecture

### Extension Pattern

All configuration modules follow a consistent pattern:

1. Import from corresponding `holosoma.config_values` module
2. Define extension-specific configs (Go2 robot, observations, etc.)
3. Register configs by updating `CORE_DEFAULTS`
4. Export for CLI access

This ensures Go2 presets are automatically available in the Tyro CLI without modifying holosoma's source code.

### Directory Structure

```
holosoma_ext/
├── config_values/          # Configuration presets
│   ├── command.py          # Go2 gait and locomotion commands
│   ├── experiment.py       # Complete training experiments
│   ├── observation.py      # Go2 observation space definitions
│   ├── reward.py           # Quadruped locomotion rewards
│   ├── robot.py            # Go2 robot hardware configuration
│   └── termination.py      # Episode termination conditions
│
├── managers/               # Custom manager terms
│   ├── command/terms/      # Quadruped gait generation (4-phase trot/walk)
│   └── reward/terms/       # Quadruped-specific rewards
│
├── data/robots/go2/        # Robot assets
│   ├── go2_12dof.urdf      # URDF model for IsaacGym
│   ├── go2_12dof.xml       # MuJoCo XML for MuJoCo simulator
│   └── dae/                # Visual meshes
│
├── utils.py                # Path resolution (@holosoma_ext/)
├── train_agent.py          # Training entry point
└── __init__.py             # Auto-registration of configs
```

## Key Features

### Quadruped Gait Manager

The extension includes a custom `LocomotionGait` command manager in `managers/command/terms/locomotion.py` that supports quadruped gaits:

- **Trot gait**: Diagonal pairs move together (FL+RR, FR+RL)
  - Phase pattern: `[0, π, π, 0]` for `[FL, FR, RL, RR]`
- **Walk gait**: Sequential leg movement
  - Phase pattern: `[0, π/2, π, 3π/2]`

The 4-phase timing is exposed as observations (`sin_phase`, `cos_phase`) to help the policy learn coordinated gaits.

### Go2 Robot Configuration

Defined in `config_values/robot.py`:

- 12 degrees of freedom (3 joints × 4 legs: hip, thigh, calf)
- Joint limits matching Go2 hardware specs
- Default standing pose
- Motor effort limits for safe operation
- Unitree SDK integration parameters

### Observation Space

Defined in `config_values/observation.py`:

```python
loco_go2_12dof = ObservationConfig(
    obs_dict={
        "actor_obs": [
            "base_ang_vel",          # 3D
            "projected_gravity",     # 3D
            "command_lin_vel",       # 2D (forward/lateral)
            "command_ang_vel",       # 1D (yaw)
            "dof_pos",              # 12D (joint positions)
            "dof_vel",              # 12D (joint velocities)
            "actions",              # 12D (last actions)
            "sin_phase",            # 4D (gait phase sine)
            "cos_phase",            # 4D (gait phase cosine)
        ]
    },
    # Total: 53 dimensions
)
```

### Reward Configuration

Quadruped-specific rewards in `config_values/reward.py`:

- Linear velocity tracking
- Angular velocity tracking
- Action smoothness
- Joint position/velocity limits
- Torque penalties
- Base orientation penalties

## Path Resolution

The extension uses the `@holosoma_ext/` prefix for asset paths, which are automatically resolved at runtime:

```python
# In robot config
asset_root="@holosoma_ext/data/robots/go2"
asset_file="@holosoma_ext/data/robots/go2/go2_12dof.urdf"
```

The `patch_asset_path_resolution()` utility in `utils.py` patches:
- IsaacGym simulator asset loading
- MuJoCo simulator asset loading
- Inference URDF resolution
- Training ONNX export

This allows the extension to reference its own assets without hardcoded paths.

## Creating Custom Experiments

### 1. Define a new experiment preset

In `config_values/experiment.py`:

```python
from holosoma.config_values.experiment import DEFAULTS as CORE_DEFAULTS
from holosoma.config_types.experiment import ExperimentConfig
from holosoma_ext.config_values import robot, observation, reward, command

my_go2_experiment = ExperimentConfig(
    robot=robot.go2_12dof,
    observation=observation.loco_go2_12dof,
    reward=reward.go2_locomotion,
    command=command.go2_locomotion,
    # ... other configs
)

CORE_DEFAULTS.update({
    "my-go2-experiment": my_go2_experiment,
})

DEFAULTS = CORE_DEFAULTS
```

### 2. Run the experiment

```bash
python -m holosoma_ext.train_agent exp:my-go2-experiment
```

## Adding New Robots

To add a new robot type to the extension:

1. **Create robot config** in `config_values/robot.py`
   - Define DOF, joint limits, default pose
   - Specify asset paths with `@holosoma_ext/` prefix

2. **Add robot assets** in `data/robots/<robot_name>/`
   - URDF file for IsaacGym
   - MuJoCo XML for MuJoCo simulator
   - Visual meshes (DAE/STL files)

3. **Define observation space** in `config_values/observation.py`
   - List observation components
   - Specify dimensions and scales

4. **Configure rewards** in `config_values/reward.py`
   - Define reward terms and weights
   - Tune for robot morphology

5. **Create experiment** in `config_values/experiment.py`
   - Combine all configs
   - Add to `CORE_DEFAULTS`

## Command-Line Options

### Training

```bash
# Basic training
python -m holosoma_ext.train_agent exp:go2-12dof

# Override gait period
python -m holosoma_ext.train_agent exp:go2-12dof \
    --command.setup_terms.locomotion_gait.params.gait_period=0.8

# Change simulator
python -m holosoma_ext.train_agent exp:go2-12dof \
    simulator:isaacsim

# Adjust actor learning rate
python -m holosoma_ext.train_agent exp:go2-12dof \
    --algo.config.actor-learning-rate=3e-4

# Use different gait type
python -m holosoma_ext.train_agent exp:go2-12dof \
    --command.setup_terms.locomotion_gait.params.phase-type=walk
```

### Inference

For running trained policies on a real Unitree Go2 robot, use the companion `holosoma_inference_ext` package:

```bash
# Install inference extension
cd src/holosoma_inference_ext
pip install -e .

# Run policy on real robot
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path=path/to/model.onnx \
    --task.use-joystick \
    --task.interface=eth0
```

## Integration with holosoma_inference_ext

The inference extension (`holosoma_inference_ext`) provides deployment capabilities:

- **Quadruped-specific phase initialization**: Correctly initializes 4-phase gait (vs 2-phase bipedal)
- **Observation dimension matching**: Ensures 53-dim observations match trained model
- **ONNX model execution**: Efficient inference with ONNX Runtime
- **Real robot deployment**: Unitree SDK integration for hardware deployment

The inference extension uses monkey-patching to override the base `LocomotionPolicy` class to support quadruped gaits without modifying the core holosoma_inference codebase.

## Technical Details

### Gait Phase Implementation

The gait manager maintains a 4D phase vector that advances each timestep:

```python
phase_tp1 = episode_length * phase_dt + phase_offset
phase = fmod(phase_tp1 + π, 2π) - π
```

During standing, all phases are set to π. When movement resumes, phases reset to the configured gait pattern.

### Asset Path Resolution

The `utils.py` module patches multiple holosoma functions to resolve `@holosoma_ext/` paths:

1. **IsaacGym**: Patches `IsaacGymSimulator.load_assets()`
2. **MuJoCo**: Patches `MujocoSceneManager.add_robot()`
3. **Inference**: Patches `resolve_holosoma_inference_path()`
4. **Export**: Patches `get_urdf_text_from_robot_config()` for ONNX export

This allows seamless integration without path configuration.

## Notes

- **Python version**: Works with Python 3.8+ (same as holosoma)
- **Simulators**: Supports both IsaacGym and MuJoCo
- **Training**: Uses core holosoma PPO implementation
- **Assets**: All paths use `@holosoma_ext/` prefix for portability
- **Gait patterns**: Trot and walk gaits supported via configuration
