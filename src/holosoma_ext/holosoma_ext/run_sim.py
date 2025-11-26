#!/usr/bin/env python3
"""
Simulation Runner with Extension Configs

This script runs simulations with the holosoma_ext configs registered.
It's a thin wrapper around holosoma.run_sim that ensures the
extension configs are loaded and @holosoma_ext/ paths are resolved.

Usage:
    python -m holosoma_ext.run_sim robot:go2-12dof terrain:flat \
        --device cuda:0
"""

import dataclasses

import tyro

import holosoma_ext  # noqa: F401
from holosoma.config_types.run_sim import RunSimConfig
from holosoma.run_sim import run_simulation
from holosoma.utils.eval_utils import init_eval_logging
from holosoma.utils.sim_utils import setup_simulator_imports
from holosoma.utils.tyro_utils import TYRO_CONIFG
from holosoma_ext.utils import patch_asset_path_resolution, resolve_robot_asset_paths


def main() -> None:
    """Launch direct simulation with extension presets."""
    init_eval_logging()
    config = tyro.cli(
        RunSimConfig,
        description="Run simulation with direct simulator control and bridge support.\n\n"
        "Usage: python -m holosoma_ext.run_sim simulator:<sim> robot:<robot> terrain:<terrain>\n"
        "Examples:\n"
        "  python -m holosoma_ext.run_sim # defaults \n"
        "  python -m holosoma_ext.run_sim simulator:mujoco robot:t1_29dof_waist_wrist terrain:terrain_locomotion_plane\n"
        "  python -m holosoma_ext.run_sim simulator:isaacgym robot:g1_29dof terrain:terrain_locomotion_mix",
        config=TYRO_CONIFG,
    )
    setup_simulator_imports(config)
    config = dataclasses.replace(config, robot=resolve_robot_asset_paths(config.robot))
    patch_asset_path_resolution()
    run_simulation(config)


if __name__ == "__main__":
    main()
