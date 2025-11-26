"""Wrapper entry point that exposes extension experiments via Tyro CLI for evaluation."""

from __future__ import annotations

import tyro

from holosoma.eval_agent import run_eval_with_tyro
from holosoma.utils.eval_utils import CheckpointConfig, init_eval_logging, load_saved_experiment_config
from holosoma.utils import config_utils
from holosoma.utils.sim_utils import setup_simulator_imports
from holosoma.utils.tyro_utils import TYRO_CONIFG
from holosoma_ext.config_values.experiment import AnnotatedExperimentConfig
from holosoma_ext.utils import patch_asset_path_resolution, resolve_robot_asset_paths


def main() -> None:
    """Launch evaluation with holosoma extension presets."""
    init_eval_logging()
    checkpoint_cfg, remaining_args = tyro.cli(CheckpointConfig, return_unknown_args=True, add_help=False)
    saved_cfg = load_saved_experiment_config(checkpoint_cfg)
    eval_cfg = saved_cfg.get_eval_config() if saved_cfg is not None else tyro._singleton.MISSING_NONPROP
    overwritten_tyro_config = tyro.cli(
        AnnotatedExperimentConfig,
        default=eval_cfg,
        args=remaining_args,
        description="Overriding config on top of what's loaded.",
        config=TYRO_CONIFG,
    )
    print("overwritten_tyro_config: ", overwritten_tyro_config)
    if hasattr(overwritten_tyro_config, "robot"):
        resolved_robot = resolve_robot_asset_paths(overwritten_tyro_config.robot)
        overwritten_tyro_config = config_utils.replace(overwritten_tyro_config, robot=resolved_robot)
    setup_simulator_imports(overwritten_tyro_config)
    patch_asset_path_resolution()
    run_eval_with_tyro(overwritten_tyro_config, checkpoint_cfg)


if __name__ == "__main__":
    main()
