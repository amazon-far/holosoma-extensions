"""Go2 robot configuration for holosoma_inference.

This module provides the robot hardware and control parameters for the Unitree Go2 quadruped.
"""

from __future__ import annotations

from holosoma_inference.config.config_types.robot import RobotConfig

# fmt: off

go2_12dof = RobotConfig(
    # Identity
    robot_type="go2_12dof",
    robot="go2",

    # SDK Configuration
    sdk_type="unitree",
    motor_type="serial",
    message_type="GO2",
    use_sensor=False,

    # Dimensions
    num_motors=12,
    num_joints=12,
    num_upper_body_joints=0,  # Quadruped has no upper body

    # Default Positions (standing pose)
    default_dof_angles=(
        0.1, 0.8, -1.5,  # FL: hip, thigh, calf
        0.1, 0.8, -1.5,  # FR: hip, thigh, calf
        -0.1, 1.0, -1.5,  # RL: hip, thigh, calf
        -0.1, 1.0, -1.5,  # RR: hip, thigh, calf
    ),
    default_motor_angles=(
        0.1, 0.8, -1.5,  # FL
        0.1, 0.8, -1.5,  # FR
        -0.1, 1.0, -1.5,  # RL
        -0.1, 1.0, -1.5,  # RR
    ),

    # Joint Limits
    joint_pos_min=(
        -1.0472, -1.5708, -2.7227,  # FL: hip, thigh, calf
        -1.0472, -1.5708, -2.7227,  # FR
        -1.0472, -0.5236, -2.7227,  # RL (rear legs have different thigh range)
        -1.0472, -0.5236, -2.7227,  # RR
    ),
    joint_pos_max=(
        1.0472, 3.4907, -0.83776,  # FL
        1.0472, 3.4907, -0.83776,  # FR
        1.0472, 4.5379, -0.83776,  # RL (rear legs have different thigh range)
        1.0472, 4.5379, -0.83776,  # RR
    ),
    joint_vel_limit=(
        30.1, 30.1, 15.70,  # FL
        30.1, 30.1, 15.70,  # FR
        30.1, 30.1, 15.70,  # RL
        30.1, 30.1, 15.70,  # RR
    ),
    motor_effort_limit=(
        23.7, 23.7, 45.43,  # FL (calf has higher torque)
        23.7, 23.7, 45.43,  # FR
        23.7, 23.7, 45.43,  # RL
        23.7, 23.7, 45.43,  # RR
    ),

    # Mappings
    motor2joint=tuple(range(12)),  # Identity mapping
    joint2motor=tuple(range(12)),  # Identity mapping
    dof_names=(
        "FL_hip_joint", "FL_thigh_joint", "FL_calf_joint",
        "FR_hip_joint", "FR_thigh_joint", "FR_calf_joint",
        "RL_hip_joint", "RL_thigh_joint", "RL_calf_joint",
        "RR_hip_joint", "RR_thigh_joint", "RR_calf_joint",
    ),
    dof_names_upper_body=(),  # No upper body for quadruped
    dof_names_lower_body=(
        "FL_hip_joint", "FL_thigh_joint", "FL_calf_joint",
        "FR_hip_joint", "FR_thigh_joint", "FR_calf_joint",
        "RL_hip_joint", "RL_thigh_joint", "RL_calf_joint",
        "RR_hip_joint", "RR_thigh_joint", "RR_calf_joint",
    ),

    # Asset Paths (reference files from holosoma_ext training package)
    asset_root="@holosoma_ext/data/robots/go2",
    asset_file="@holosoma_ext/data/robots/go2/go2_12dof.urdf",
    robot_scene_xml="@holosoma_ext/data/robots/go2/go2_12dof.xml",

    # Link Names
    torso_link_name="base",
    left_hand_link_name=None,  # Quadruped has no hands
    right_hand_link_name=None,

    # Unitree-Specific Constants (for Go2)
    unitree_legged_const={
        "HIGHLEVEL": 238,
        "LOWLEVEL": 255,
        "TRIGERLEVEL": 240,
        "PosStopF": 2146000000.0,
        "VelStopF": 16000.0,
        "MODE_MACHINE": 5,
        "MODE_PR": 0,
    },
    weak_motor_joint_index={
        "FL_hip_joint": 0, "FL_thigh_joint": 1, "FL_calf_joint": 2,
        "FR_hip_joint": 3, "FR_thigh_joint": 4, "FR_calf_joint": 5,
        "RL_hip_joint": 6, "RL_thigh_joint": 7, "RL_calf_joint": 8,
        "RR_hip_joint": 9, "RR_thigh_joint": 10, "RR_calf_joint": 11,
    },
    motion={"body_name_ref": ["base"]},
)

# =============================================================================
# Default Configurations Dictionary
# =============================================================================

DEFAULTS = {
    "go2-12dof": go2_12dof,
}
"""Dictionary of Go2 robot configurations.

Keys use hyphen-case naming convention for CLI compatibility.
"""

# fmt: on

__all__ = ["go2_12dof", "DEFAULTS"]
