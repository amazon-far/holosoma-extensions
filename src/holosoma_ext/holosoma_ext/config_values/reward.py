"""Reward presets that layer terrain height terms onto the holosoma defaults."""

from __future__ import annotations

from holosoma.config_values.reward import DEFAULTS as CORE_DEFAULTS
from holosoma.config_types.reward import RewardManagerCfg, RewardTermCfg

# GO2 12DOF Locomotion reward manager
go2_12dof_loco = RewardManagerCfg(
    only_positive_rewards=False,
    terms={
        # Tracking rewards (main task objectives)
        "tracking_lin_vel": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:tracking_lin_vel",
            weight=5.0,
            params={
                "tracking_sigma": 0.25,
            },
        ),
        "tracking_ang_vel": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:tracking_ang_vel",
            weight=1.5,
            params={
                "tracking_sigma": 0.25,
            },
        ),
        # Gait rewards
        "feet_phase": RewardTermCfg(
            func="holosoma_ext.managers.reward.terms.locomotion:feet_phase",
            weight=5.0,
            params={
                "swing_height": 0.09,
                "tracking_sigma": 0.008,
            },
        ),
        # Penalty rewards (regularization)
        "penalty_ang_vel_xy": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:penalty_ang_vel_xy",
            weight=-1.0,
            params={},
            tags=["penalty_curriculum"],
        ),
        "penalty_orientation": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:penalty_orientation",
            weight=-10.0,
            params={},
            tags=["penalty_curriculum"],
        ),
        "penalty_action_rate": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:penalty_action_rate",
            weight=-1.0,
            params={},
            tags=["penalty_curriculum"],
        ),
        "penalty_close_feet_xy": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:penalty_close_feet_xy",
            weight=-0.0,
            params={
                "close_feet_threshold": 0.15,
            },
            tags=["penalty_curriculum"],
        ),
        # Alive reward
        "alive": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:alive",
            weight=1.0,
            params={},
        ),
        # Pose maintenance
        "pose": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:pose",
            weight=-5.0,
            params={
                "pose_weights": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            },
            tags=["penalty_curriculum"],
        ),
        # Base height
        "base_height": RewardTermCfg(
            func="holosoma.managers.reward.terms.locomotion:base_height",
            weight=-10.0,
            params={
                "desired_base_height": 0.25,
                "zero_vel_penalty_scale": 10.0,
            },
            tags=["penalty_curriculum"],
        ),
        "penalty_collision": RewardTermCfg(
            func="holosoma_ext.managers.reward.terms.locomotion:penalty_collision",
            weight=-10.0,
            params={
                "penalize_contacts_on": [
                    "FL_thigh",
                    "FR_thigh",
                    "RL_thigh",
                    "RR_thigh",
                    "FL_calf",
                    "FR_calf",
                    "RL_calf",
                    "RR_calf",
                ]
            },
            tags=["penalty_curriculum"],
        ),
    },
)

CORE_DEFAULTS.update(
    {
        "go2_12dof_loco": go2_12dof_loco,
    }
)

DEFAULTS = CORE_DEFAULTS

__all__ = [
    "DEFAULTS",
    "go2_12dof_loco",
]
