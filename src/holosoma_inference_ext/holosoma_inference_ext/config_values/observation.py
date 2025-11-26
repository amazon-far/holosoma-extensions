"""Go2 observation configuration for holosoma_inference.

This module provides the observation space configuration for the Unitree Go2 quadruped
during locomotion tasks.
"""

from __future__ import annotations

from holosoma_inference.config.config_types.observation import ObservationConfig

# =============================================================================
# Go2 Locomotion Observation Configuration
# =============================================================================

loco_go2_12dof = ObservationConfig(
    obs_dict={
        "actor_obs": [
            "base_ang_vel",
            "projected_gravity",
            "command_lin_vel",
            "command_ang_vel",
            "dof_pos",
            "dof_vel",
            "actions",
            "sin_phase",
            "cos_phase",
        ]
    },
    obs_dims={
        "base_lin_vel": 3,
        "base_ang_vel": 3,
        "projected_gravity": 3,
        "command_lin_vel": 2,
        "command_ang_vel": 1,
        "dof_pos": 12,  # Go2 has 12 DOF
        "dof_vel": 12,
        "actions": 12,
        "sin_phase": 4,
        "cos_phase": 4,
    },
    obs_scales={
        "base_lin_vel": 2.0,
        "base_ang_vel": 0.25,
        "projected_gravity": 1.0,
        "command_lin_vel": 2.0,  # Commands scaled by 2.0
        "command_ang_vel": 0.25,
        "dof_pos": 1.0,
        "dof_vel": 0.05,
        "actions": 1.0,
        "sin_phase": 1.0,
        "cos_phase": 1.0,
    },
    history_length_dict={
        "actor_obs": 1,
    },
)

# =============================================================================
# Default Configurations Dictionary
# =============================================================================

DEFAULTS = {
    "loco-go2-12dof": loco_go2_12dof,
}
"""Dictionary of Go2 observation configurations.

Keys use hyphen-case naming convention for CLI compatibility.
"""

__all__ = ["loco_go2_12dof", "DEFAULTS"]
