"""Go2 inference configurations for holosoma_inference_ext."""

from __future__ import annotations

from holosoma_inference.config.config_types.inference import InferenceConfig
from holosoma_inference.config.config_values import task
from holosoma_inference_ext.config_values import observation, robot

# Go2 Locomotion
go2_12dof_loco = InferenceConfig(
    robot=robot.go2_12dof,
    observation=observation.loco_go2_12dof,
    task=task.locomotion,
)

DEFAULTS = {
    "go2-12dof-loco": go2_12dof_loco,
}
"""Dictionary of Go2 inference configurations.

Keys use hyphen-case naming convention for CLI compatibility.
"""

__all__ = ["go2_12dof_loco", "DEFAULTS"]
