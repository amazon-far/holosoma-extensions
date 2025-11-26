"""Reward terms that reuse legacy locomotion helpers."""

from __future__ import annotations

import torch
from holosoma.managers.reward.terms.locomotion import _expected_foot_height


def feet_phase(env, swing_height: float = 0.08, tracking_sigma: float = 0.25) -> torch.Tensor:
    """Reward for tracking desired foot height based on gait phase for quadrupeds.

    This version properly handles 4-legged robots (quadrupeds) by tracking all 4 feet
    instead of just 2 feet like the bipedal version in holosoma.

    Args:
        env: The environment instance
        swing_height: Maximum height during swing phase
        tracking_sigma: Sigma for exponential reward scaling

    Returns:
        Reward tensor [num_envs]
    """
    # Get foot heights (relative to terrain) for all 4 feet
    feet_heights = env.terrain_manager.get_state("locomotion_terrain").feet_heights
    num_feet = feet_heights.shape[1]

    # Ensure we have 4 feet for quadruped
    assert num_feet == 4, f"Expected 4 feet for quadruped, but got {num_feet}"

    # Get gait phases for all feet
    gait_state = env.command_manager.get_state("locomotion_gait")

    # Calculate expected foot heights based on phase for each foot
    total_error = torch.zeros(feet_heights.shape[0], device=feet_heights.device)
    for i in range(num_feet):
        foot_z = feet_heights[:, i]
        expected_z = _expected_foot_height(gait_state.phase[:, i], swing_height)
        error = torch.square(foot_z - expected_z)
        total_error += error

    # Apply exponential reward
    return torch.exp(-total_error / tracking_sigma)


def penalty_collision(env, penalize_contacts_on: list) -> torch.Tensor:
    """Penalize collisions on selected bodies.

    Args:
        env: The environment instance
        penalize_contacts_on: List of body names to penalize contacts on

    Returns:
        Reward tensor [num_envs]
    """
    if penalize_contacts_on is None:
        raise ValueError("penalize_contacts_on parameter is required for penalty_collision reward term")

    # Convert names to indices
    penalized_indices = [env.simulator.find_rigid_body_indice(name) for name in penalize_contacts_on]

    # Penalize collisions on selected bodies
    return torch.sum(torch.norm(env.simulator.contact_forces[:, penalized_indices, :], dim=-1) > 1.0, dim=-1)