# Setup Scripts

This directory contains setup and source scripts for different simulation environments.

## Setup Scripts (One-time Installation)

These scripts set up conda environments and install dependencies. Run once per environment.

### IsaacGym (for training)

```bash
# Sets up conda environment 'hsgym' and installs holosoma_ext
bash scripts/setup_isaacgym.sh
```

### IsaacSim (for training)

```bash
# Sets up conda environment 'hssim' and installs holosoma_ext
bash scripts/setup_isaacsim.sh
```

### MuJoCo (for training)

```bash
# Sets up conda environment 'hsmujoco' and installs holosoma_ext
bash scripts/setup_mujoco.sh
```

### Inference (for deployment)

```bash
# Sets up conda environment 'hsinference' and installs holosoma_inference_ext
bash scripts/setup_inference.sh
```

## Source Scripts (Activate Environment)

These scripts activate the conda environment and set up paths. Source before running commands.

### Training with IsaacGym

```bash
source scripts/source_isaacgym_setup.sh
python -m holosoma_ext.train_agent exp:go2-12dof-loco
```

### Training with IsaacSim

```bash
source scripts/source_isaacsim_setup.sh
python -m holosoma_ext.train_agent exp:go2-12dof-loco simulator:isaacsim
```

### Training with MuJoCo

```bash
source scripts/source_mujoco_setup.sh
python -m holosoma_ext.train_agent exp:go2-12dof-loco simulator:mujoco
```

### Inference/Deployment

```bash
source scripts/source_inference_setup.sh
python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
    --task.model-path=path/to/model.onnx
```

## Environment Names

| Script | Conda Environment | Purpose |
|--------|------------------|---------|
| `setup_isaacgym.sh` | `hsgym` | Training with IsaacGym |
| `setup_isaacsim.sh` | `hssim` | Training with IsaacSim |
| `setup_mujoco.sh` | `hsmujoco` | Training with MuJoCo |
| `setup_inference.sh` | `hsinference` | Policy deployment |

## Notes

- All scripts automatically call the corresponding holosoma setup scripts
- Source scripts work with both bash and zsh
- Setup scripts install the extension packages in editable mode (`pip install -e .`)
- Always source the appropriate environment before running training or inference
