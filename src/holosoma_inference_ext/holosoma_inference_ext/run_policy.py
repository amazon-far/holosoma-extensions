#!/usr/bin/env python3
"""
Policy Runner with Extension Configs

This script runs policies with the holosoma_inference_ext configs registered.
It's a thin wrapper around holosoma_inference.run_policy that ensures the
extension configs are loaded and @holosoma_ext/ paths are resolved.

Usage:
    python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
        --task.model-path path/to/model.onnx

    python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
        --task.model-path wandb://project/run/model.onnx

    python -m holosoma_inference_ext.run_policy inference:go2-12dof-loco \
        --task.model-path ./model.onnx \
        --task.deploy-mode real
"""

# Patch path resolution and import configs
from holosoma_ext.utils import patch_asset_path_resolution

patch_asset_path_resolution()

import tyro
from typing_extensions import Annotated

import holosoma_inference_ext  # noqa: F401 - applies monkey patches for quadruped
from holosoma_inference.config.config_types.inference import InferenceConfig
from holosoma_inference.config.config_values import inference as core_inference
from holosoma_inference.config.utils import TYRO_CONFIG
from holosoma_inference.policies.locomotion import LocomotionPolicy  # Gets the patched quadruped version
from holosoma_inference.policies.wbt import WholeBodyTrackingPolicy
from holosoma_inference_ext.config_values import inference as ext_inference


def main():
    # Merge core and extension defaults for Tyro subcommands
    merged_defaults = {**core_inference.DEFAULTS, **ext_inference.DEFAULTS}
    subcommands = {f"inference:{k}": v for k, v in merged_defaults.items()}
    annotated_cfg = Annotated[
        InferenceConfig,
        tyro.conf.arg(constructor=tyro.extras.subcommand_type_from_defaults(subcommands)),
    ]

    config = tyro.cli(annotated_cfg, config=TYRO_CONFIG)
    actor_obs = config.observation.obs_dict.get("actor_obs", [])
    policy_class = WholeBodyTrackingPolicy if "motion_command" in actor_obs else LocomotionPolicy
    policy_class(config=config).run()


if __name__ == "__main__":
    main()
