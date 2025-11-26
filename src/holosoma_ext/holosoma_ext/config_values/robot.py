"""Observation presets that incorporate extension-defined terms."""

from __future__ import annotations

from holosoma.config_types.robot import (
    RobotAssetConfig,
    RobotBridgeConfig,
    RobotConfig,
    RobotControlConfig,
    RobotInitState,
)

from holosoma.config_values.robot import DEFAULTS as CORE_DEFAULTS

go2_12dof = RobotConfig(
    num_bodies=17,
    dof_obs_size=12,
    actions_dim=12,
    policy_obs_dim=-1,
    critic_obs_dim=-1,
    algo_obs_dim_dict={},
    key_bodies=["FL_foot_contact_point", "FR_foot_contact_point", "RL_foot_contact_point", "RR_foot_contact_point"],
    num_feet=4,
    foot_body_name="foot",
    foot_height_name="foot_contact_point",
    torso_name="base",
    contact_pairs_multiplier=1,
    knee_name="",
    knee_dof_names=[],
    hips_dof_names=[],
    dof_names=[
        "FL_hip_joint", "FL_thigh_joint", "FL_calf_joint",
        "FR_hip_joint", "FR_thigh_joint", "FR_calf_joint",
        "RL_hip_joint", "RL_thigh_joint", "RL_calf_joint",
        "RR_hip_joint", "RR_thigh_joint", "RR_calf_joint"
    ],
    upper_dof_names=[],
    upper_left_arm_dof_names=[],
    upper_right_arm_dof_names=[],
    lower_dof_names=[
        "FL_hip_joint", "FL_thigh_joint", "FL_calf_joint",
        "FR_hip_joint", "FR_thigh_joint", "FR_calf_joint",
        "RL_hip_joint", "RL_thigh_joint", "RL_calf_joint",
        "RR_hip_joint", "RR_thigh_joint", "RR_calf_joint"
    ],
    has_torso=True,
    has_upper_body_dof=False,
    left_ankle_dof_names=[],
    right_ankle_dof_names=[],
    dof_pos_lower_limit_list=[
        -1.0472, -1.5708, -2.7227,  # FL
        -1.0472, -1.5708, -2.7227,  # FR
        -1.0472, -0.5236, -2.7227,  # RL
        -1.0472, -0.5236, -2.7227   # RR
    ],
    dof_pos_upper_limit_list=[
        1.0472, 3.4907, -0.83776,   # FL
        1.0472, 3.4907, -0.83776,   # FR
        1.0472, 4.5379, -0.83776,   # RL
        1.0472, 4.5379, -0.83776    # RR
    ],
    dof_vel_limit_list=[
        30.1, 30.1, 15.70,
        30.1, 30.1, 15.70,
        30.1, 30.1, 15.70,
        30.1, 30.1, 15.70
    ],
    dof_effort_limit_list=[
        23.7, 23.7, 45.43,
        23.7, 23.7, 45.43,
        23.7, 23.7, 45.43,
        23.7, 23.7, 45.43
    ],
    dof_armature_list=[
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
    ],  # right wrist
    dof_joint_friction_list=[
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ],
    body_names=[
        "base",
        "FL_hip", "FL_thigh", "FL_calf", "FL_foot", "FL_foot_contact_point",
        "FR_hip", "FR_thigh", "FR_calf", "FR_foot", "FR_foot_contact_point",
        "Head_upper", "Head_lower",
        "RL_hip", "RL_thigh", "RL_calf", "RL_foot", "RL_foot_contact_point",
        "RR_hip", "RR_thigh", "RR_calf", "RR_foot", "RR_foot_contact_point"
    ],
    terminate_after_contacts_on=[
        "base",
        "Head_upper",
        "Head_lower"
    ],
    penalize_contacts_on=[ # TODO: Remove this from the robot config since it's in the reward config
        "FL_thigh", "FR_thigh", "RL_thigh", "RR_thigh",
        "FL_calf", "FR_calf", "RL_calf", "RR_calf",
    ],
    init_state=RobotInitState(
        pos=[0.0, 0.0, 0.42],  # x,y,z [m]
        rot=[0.0, 0.0, 0.0, 1.0],  # x,y,z,w [quat]
        lin_vel=[0.0, 0.0, 0.0],  # x,y,z [m/s]
        ang_vel=[0.0, 0.0, 0.0],  # x,y,z [rad/s]
        default_joint_angles={
            "FL_hip_joint": 0.1,
            "FL_thigh_joint": 0.8,
            "FL_calf_joint": -1.5,
            "FR_hip_joint": 0.1,
            "FR_thigh_joint": 0.8,
            "FR_calf_joint": -1.5,
            "RL_hip_joint": -0.1,
            "RL_thigh_joint": 1.0,
            "RL_calf_joint": -1.5,
            "RR_hip_joint": -0.1,
            "RR_thigh_joint": 1.0,
            "RR_calf_joint": -1.5,
        },
    ),
    randomize_link_body_names=[
        "base",
        "FL_hip", "FL_thigh", "FL_calf",
        "FR_hip", "FR_thigh", "FR_calf",
        "RL_hip", "RL_thigh", "RL_calf",
        "RR_hip", "RR_thigh", "RR_calf"
    ],
    
    symmetry_joint_names={
        "FL_hip_joint": "FR_hip_joint", # fl_hip_joint
        "FL_thigh_joint": "FR_thigh_joint", # fl_thigh_joint
        "FL_calf_joint": "FR_calf_joint", # fl_calf_joint
        "FR_hip_joint": "FL_hip_joint", # fr_hip_joint
        "FR_thigh_joint": "FL_thigh_joint", # fr_thigh_joint
        "FR_calf_joint": "FL_calf_joint", # fr_calf_joint
        "RL_hip_joint": "RR_hip_joint", # rl_hip_joint
        "RL_thigh_joint": "RR_thigh_joint", # rl_thigh_joint
        "RL_calf_joint": "RR_calf_joint", # rl_calf_joint
        "RR_hip_joint": "RL_hip_joint", # rr_hip_joint
        "RR_thigh_joint": "RL_thigh_joint", # rr_thigh_joint
        "RR_calf_joint": "RL_calf_joint", # rr_calf_joint
    },
    flip_sign_joint_names=[
        "FL_hip_joint", "FR_hip_joint", "RL_hip_joint", "RR_hip_joint",
    ],
    apply_dof_armature_in_isaacgym=True,
    control=RobotControlConfig(
        control_type="P",
        stiffness={
            "FL_hip_joint": 20,
            "FL_thigh_joint": 20,
            "FL_calf_joint": 20,
            "FR_hip_joint": 20,
            "FR_thigh_joint": 20,
            "FR_calf_joint": 20,
            "RL_hip_joint": 20,
            "RL_thigh_joint": 20,
            "RL_calf_joint": 20,
            "RR_hip_joint": 20,
            "RR_thigh_joint": 20,
            "RR_calf_joint": 20,
        },
        damping={
            "FL_hip_joint": 0.5,
            "FL_thigh_joint": 0.5,
            "FL_calf_joint": 0.5,
            "FR_hip_joint": 0.5,
            "FR_thigh_joint": 0.5,
            "FR_calf_joint": 0.5,
            "RL_hip_joint": 0.5,
            "RL_thigh_joint": 0.5,
            "RL_calf_joint": 0.5,
            "RR_hip_joint": 0.5,
            "RR_thigh_joint": 0.5,
            "RR_calf_joint": 0.5,
        },
        action_scale=0.25,  # 0.25 for locomotion, 1.0 for whole body tracking
        action_clip_value=100.0,
        clip_actions=True,
        clip_torques=True,
    ),
    asset=RobotAssetConfig(
        asset_root="@holosoma_ext/data/robots",
        collapse_fixed_joints=True,
        replace_cylinder_with_capsule=True,
        flip_visual_attachments=True,
        armature=0.001,
        thickness=0.01,
        max_angular_velocity=1000.0,
        max_linear_velocity=1000.0,
        angular_damping=0.0,
        linear_damping=0.0,
        urdf_file="go2/go2_12dof.urdf",
        usd_file=None,
        xml_file="go2/go2_12dof.xml",
        robot_type="go2_12dof",
        enable_self_collisions=True,
        default_dof_drive_mode=3,
        fix_base_link=False,
    ),
    bridge=RobotBridgeConfig(
        sdk_type="unitree",
        motor_type="serial",
    ),
)

CORE_DEFAULTS.update(
    {
        "go2_12dof": go2_12dof,
    }
)

DEFAULTS = CORE_DEFAULTS

__all__ = [
    "DEFAULTS",
    "go2_12dof",
]
