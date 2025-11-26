"""Wrapper entry point that exposes extension experiments via Tyro CLI."""

from __future__ import annotations

import tyro

from holosoma.train_agent import train
from holosoma.utils.sim_utils import setup_simulator_imports
from holosoma.utils.tyro_utils import TYRO_CONIFG
from holosoma_ext.config_values.experiment import AnnotatedExperimentConfig
from holosoma_ext.utils import patch_asset_path_resolution, resolve_robot_asset_paths


def main() -> None:
    """Launch training with holosoma extension presets."""
    tyro_cfg = tyro.cli(AnnotatedExperimentConfig, config=TYRO_CONIFG)
    # Import simulator dependencies first
    setup_simulator_imports(tyro_cfg)
    # Apply asset path resolution patches AFTER simulator is imported
    patch_asset_path_resolution()
    # Resolve robot asset paths on the parsed config (dataclass -> replace via asdict/constructor)
    resolved_robot = resolve_robot_asset_paths(tyro_cfg.robot)
    tyro_cfg = type(tyro_cfg)(**{**tyro_cfg.__dict__, "robot": resolved_robot})
    train(tyro_cfg)


if __name__ == "__main__":
    main()
