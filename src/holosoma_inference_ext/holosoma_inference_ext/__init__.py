"""Holosoma Inference Extension - Go2 Quadruped Support.

This package extends holosoma_inference with support for the Unitree Go2 quadruped robot.

It provides:
- Robot configuration (holosoma_inference_ext.config_values.robot)
- Observation configuration (holosoma_inference_ext.config_values.observation)
- Robot models (data/robots/go2/)

The configurations are registered automatically and can be used with holosoma_inference
policies once this package is installed.
"""

from __future__ import annotations

__version__ = "0.1.0"

# Register Go2 configs with holosoma_inference
try:
    from holosoma_inference.config import config_values as core_config_values
    from holosoma_inference_ext.config_values import inference, observation, robot

    # Merge Go2 configs into core DEFAULTS
    core_config_values.robot.DEFAULTS.update(robot.DEFAULTS)
    core_config_values.observation.DEFAULTS.update(observation.DEFAULTS)
    core_config_values.inference.DEFAULTS.update(inference.DEFAULTS)

except ImportError:
    # holosoma_inference not yet installed, configs will be available after installation
    pass

# ----------------------------------------------------------------------
# Override locomotion phase handling for quadruped 4-dim sin/cos output.
# ----------------------------------------------------------------------
try:
    import numpy as np
    from holosoma_inference.policies import base as _base_mod
    from holosoma_inference.policies import locomotion as _loco_mod
    from holosoma_inference import run_policy as _run_policy_mod

    _LocomotionPolicyBase = _loco_mod.LocomotionPolicy

    class LocomotionPolicy(_LocomotionPolicyBase):  # type: ignore[misc]
        def _init_phase_components(self):
            """Initialize four-phase gait timing (FL, FR, RL, RR)."""
            self.use_phase = self.config.task.use_phase
            if self.use_phase:
                # Get gait type from config (defaults to trot)
                phase_type = getattr(self.config.task, 'phase_type', 'trot')

                self.phase = np.zeros((1, 4))
                # Set phase offsets based on gait type
                if phase_type == 'trot':
                    # Trot: diagonal pairs (FL+RR, FR+RL)
                    self.phase[:, 0] = 0.0      # FL - Front Left
                    self.phase[:, 1] = np.pi    # FR - Front Right
                    self.phase[:, 2] = np.pi    # RL - Rear Left
                    self.phase[:, 3] = 0.0      # RR - Rear Right
                elif phase_type == 'walk':
                    # Walk: sequential leg movement
                    self.phase[:, 0] = 0.0          # FL
                    self.phase[:, 1] = 0.5 * np.pi  # FR
                    self.phase[:, 2] = np.pi        # RL
                    self.phase[:, 3] = 1.5 * np.pi  # RR
                else:
                    raise ValueError(f"Unknown phase_type: {phase_type}. Use 'trot' or 'walk'.")

                self.phase_dt = 2 * np.pi / (self.rl_rate * self.gait_period)
                self.is_standing = False
                self.phase_type = phase_type  # Store for later use

        def _handle_start_policy(self):
            """Handle start policy action - override to use quadruped phase."""
            self.use_policy_action = True
            self.get_ready_state = False
            self.logger.info("Using policy actions")
            # Reset to configured quadruped gait pattern
            if self.use_phase:
                if self.phase_type == 'trot':
                    self.phase = np.array([[0.0, np.pi, np.pi, 0.0]])
                elif self.phase_type == 'walk':
                    self.phase = np.array([[0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi]])

        def update_phase_time(self):
            if not self.use_phase:
                return
            phase_tp1 = self.phase + self.phase_dt
            self.phase = np.fmod(phase_tp1 + np.pi, 2 * np.pi) - np.pi
            if np.linalg.norm(self.lin_vel_command[0]) < 0.01 and np.linalg.norm(self.ang_vel_command[0]) < 0.01:
                self.phase[:, :] = np.pi
                self.is_standing = True
            elif self.is_standing:
                # Reset to configured gait pattern when resuming from standing
                if self.phase_type == 'trot':
                    self.phase = np.array([[0.0, np.pi, np.pi, 0.0]])
                elif self.phase_type == 'walk':
                    self.phase = np.array([[0.0, 0.5 * np.pi, np.pi, 1.5 * np.pi]])
                self.is_standing = False

    _loco_mod.LocomotionPolicy = LocomotionPolicy  # type: ignore[assignment]
    _run_policy_mod.LocomotionPolicy = LocomotionPolicy  # type: ignore[assignment]

except ImportError:
    pass

__all__ = ["__version__"]
