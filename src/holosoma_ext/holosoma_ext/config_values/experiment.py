"""Experiment presets combining holosoma and extension terrain locomotion components."""

from __future__ import annotations

from dataclasses import replace

import tyro
from typing_extensions import Annotated

from holosoma.config_types.experiment import ExperimentConfig, NightlyConfig, TrainingConfig

from holosoma.config_types.experiment import ExperimentConfig
from holosoma.config_values.experiment import DEFAULTS as CORE_DEFAULTS
from holosoma.config_values.logger import wandb as core_wandb_logger
from holosoma.config_values import (
    algo,
    terrain,
    action,
    randomization,
    curriculum,
    observation
)
from holosoma_ext.config_values import (
    robot,
    termination,
    command,
    reward
)

# ================================================================================================
# Go2 locomotion experiment
# ================================================================================================

go2_12dof = ExperimentConfig(
    env_class="holosoma.envs.locomotion.locomotion_manager.LeggedRobotLocomotionManager",
    training=TrainingConfig(project="hv-go2-manager", name="go2_12dof_manager"),
    algo=replace(algo.ppo, config=replace(algo.ppo.config, num_learning_iterations=25000, use_symmetry=True)),
    robot=robot.go2_12dof,
    terrain=terrain.terrain_locomotion_mix,
    observation=observation.g1_29dof_loco_single_wolinvel, # same observation as G1
    action=action.g1_29dof_joint_pos, # same joint position control as G1
    termination=termination.go2_12dof,
    randomization=randomization.g1_29dof_randomization, # same randomization as G1
    command=command.go2_12dof_command,
    curriculum=curriculum.g1_29dof_curriculum, # same curriculum as G1
    reward=reward.go2_12dof_loco,
    nightly=NightlyConfig(
        iterations=5000,
        metrics={"Episode/rew_tracking_ang_vel": [0.7, "inf"], "Episode/rew_tracking_lin_vel": [0.55, "inf"]},
    ),
)


DEFAULTS = {
    **CORE_DEFAULTS,
    "go2_12dof": go2_12dof,
}


AnnotatedExperimentConfig = Annotated[
    ExperimentConfig,
    tyro.conf.arg(
        constructor=tyro.extras.subcommand_type_from_defaults(
            {f"exp:{name.replace('_', '-')}": cfg for name, cfg in DEFAULTS.items()}
        )
    ),
]
