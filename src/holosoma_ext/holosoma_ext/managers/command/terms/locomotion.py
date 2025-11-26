"""Locomotion command term with straight-command oversampling support."""

from __future__ import annotations

from typing import Any, Sequence, cast

from holosoma.managers.command.terms.locomotion import LocomotionGait as CoreLocomotionGait
from holosoma.managers.command.terms.locomotion import LocomotionCommand as CoreLocomotionCommand
from holosoma.utils.safe_torch_import import torch
from holosoma.utils.torch_utils import torch_rand_float

LocomotionCommand = CoreLocomotionCommand

class LocomotionGait(CoreLocomotionGait):
    """Stateful term that owns gait phase buffers and updates them each step."""

    def __init__(self, cfg: Any, env: Any):
        super().__init__(cfg, env)

        params = cfg.params or {}

        self.phase_type = params.get("phase_type")

    def setup(self) -> None:
        env = self.env
        device = env.device
        num_envs = env.num_envs

        self.phase_offset = torch.zeros((num_envs, 4), dtype=torch.float32, device=device)
        self.phase = torch.zeros((num_envs, 4), dtype=torch.float32, device=device)
        self.gait_freq = torch.zeros((num_envs, 1), dtype=torch.float32, device=device)
        self.phase_dt = torch.zeros((num_envs, 1), dtype=torch.float32, device=device)

        self._initialize_indices(None, evaluating=env.is_evaluating)

    def reset(self, env_ids: torch.Tensor | None) -> None:
        self._initialize_indices(env_ids, evaluating=self.env.is_evaluating)

    def step(self) -> None:
        if self.phase is None or self.phase_offset is None or self.phase_dt is None:
            return

        env = self.env
        phase_tp1 = env.episode_length_buf.unsqueeze(1) * self.phase_dt + self.phase_offset
        self.phase.copy_(torch.fmod(phase_tp1 + torch.pi, 2 * torch.pi) - torch.pi)

        command_tensor = getattr(self.manager, "commands", None) if hasattr(self, "manager") else None
        if command_tensor is None:
            return

        stand_mask = torch.logical_and(
            torch.linalg.norm(command_tensor[:, :2], dim=1) < 0.01,
            torch.abs(command_tensor[:, 2]) < 0.01,
        )
        if stand_mask.any():
            self.phase[stand_mask] = torch.full(
                (int(stand_mask.sum().item()), 4), self.stand_phase_value, device=env.device
            )

    # ------------------------------------------------------------------ #
    # Internal utilities
    # ------------------------------------------------------------------ #

    def _initialize_indices(self, env_ids: torch.Tensor | None, *, evaluating: bool) -> None:
        if self.phase_offset is None or self.phase is None or self.gait_freq is None or self.phase_dt is None:
            return

        idx = self._ensure_index_tensor(env_ids)
        if idx.numel() == 0:
            return

        if self.phase_type == "trot":
            self.phase_type_values = [0, torch.pi, torch.pi, 0]
        elif self.phase_type == "walk":
            self.phase_type_values = [0, 0.5 * torch.pi, torch.pi, 1.5 * torch.pi]
        else:
            raise ValueError(f"Invalid phase type: {self.phase_type}")

        if evaluating:
            # Fixed phases for evaluation
            self.phase_offset[idx, 0] = self.phase_type_values[0]
            self.phase_offset[idx, 1] = self.phase_type_values[1]  # Front right at 90°
            self.phase_offset[idx, 2] = self.phase_type_values[2]  # Rear left at 180°
            self.phase_offset[idx, 3] = self.phase_type_values[3]  # Rear right at 270° (or -90°)
        else:
            # Randomize the starting phase for the first leg
            self.phase_offset[idx, 0] = torch_rand_float(
                -torch.pi, torch.pi, (idx.shape[0], 1), device=self.env.device
            ).squeeze(1)
            delta_1 = self.phase_type_values[1] - self.phase_type_values[0]
            delta_2 = self.phase_type_values[2] - self.phase_type_values[0]
            delta_3 = self.phase_type_values[3] - self.phase_type_values[0]
            # Set remaining legs apart for quadruped gait
            # Typical pattern: FL, FR, RL, RR or similar
            self.phase_offset[idx, 1] = torch.fmod(self.phase_offset[idx, 0] + delta_1 + torch.pi, 2 * torch.pi) - torch.pi
            self.phase_offset[idx, 2] = torch.fmod(self.phase_offset[idx, 0] + delta_2 + torch.pi, 2 * torch.pi) - torch.pi
            self.phase_offset[idx, 3] = torch.fmod(self.phase_offset[idx, 0] + delta_3 + torch.pi, 2 * torch.pi) - torch.pi

        self.phase[idx] = self.phase_offset[idx]
        self.resample_frequency(idx)