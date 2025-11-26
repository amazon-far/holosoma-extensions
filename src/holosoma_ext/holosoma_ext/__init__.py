"""Extension scaffolding for holosoma experiments."""

from __future__ import annotations

from importlib import import_module

from holosoma.utils.safe_torch_import import torch
from holosoma_ext.utils import patch_asset_path_resolution

# Register extension configs with core holosoma
try:
    # Import config modules to trigger DEFAULTS updates
    from holosoma_ext.config_values import command, experiment, reward, robot, termination  # noqa: F401
except ImportError:
    # Core holosoma not available yet
    pass

# --------------------------------------------------------------------------------------
# Restore holosoma features that were removed upstream but required by extension presets.
# --------------------------------------------------------------------------------------
try:  # pragma: no cover - depends on holosoma runtime
    from typing import TYPE_CHECKING

    from holosoma.agents.modules.augmentation_utils import SymmetryUtils

    if TYPE_CHECKING:
        _SymmetryUtilsType = type[SymmetryUtils]
    else:
        _SymmetryUtilsType = type(SymmetryUtils)  # type: ignore[misc]
except ModuleNotFoundError:  # holosoma not available in the environment
    SymmetryUtils = None  # type: ignore[misc,assignment]
    _SymmetryUtilsType = None  # type: ignore[misc,assignment]


def _patch_phase_mirroring() -> None:
    """Override phase mirroring to swap left/right leg phases completely."""
    if SymmetryUtils is None:
        return

    def mirror_obs_sin_phase(self, sin_phase: torch.Tensor) -> torch.Tensor:
        """Mirrors the sine phase for gait timing by swapping left/right legs.

        Parameters
        ----------
        sin_phase : torch.Tensor
            Sine of gait phase with layout [sin(φ_FL), sin(φ_FR), sin(φ_RL), sin(φ_RR)].
            Where FL=Front Left, FR=Front Right, RL=Rear Left, RR=Rear Right.

        Returns
        -------
        torch.Tensor
            Mirrored phase with left/right swapped: [sin(φ_FR), sin(φ_FL), sin(φ_RR), sin(φ_RL)].
        """
        if sin_phase.shape[-1] == 4:
            # Quadruped: swap FL<->FR and RL<->RR
            return sin_phase[..., [1, 0, 3, 2]]
        elif sin_phase.shape[-1] == 2:
            # Biped: swap left<->right
            return sin_phase[..., [1, 0]]
        else:
            # Fallback: return as-is for unexpected dimensions
            return sin_phase

    def mirror_obs_cos_phase(self, cos_phase: torch.Tensor) -> torch.Tensor:
        """Mirrors the cosine phase for gait timing by swapping left/right legs.

        Parameters
        ----------
        cos_phase : torch.Tensor
            Cosine of gait phase with layout [cos(φ_FL), cos(φ_FR), cos(φ_RL), cos(φ_RR)].
            Where FL=Front Left, FR=Front Right, RL=Rear Left, RR=Rear Right.

        Returns
        -------
        torch.Tensor
            Mirrored phase with left/right swapped: [cos(φ_FR), cos(φ_FL), cos(φ_RR), cos(φ_RL)].
        """
        if cos_phase.shape[-1] == 4:
            # Quadruped: swap FL<->FR and RL<->RR
            return cos_phase[..., [1, 0, 3, 2]]
        elif cos_phase.shape[-1] == 2:
            # Biped: swap left<->right
            return cos_phase[..., [1, 0]]
        else:
            # Fallback: return as-is for unexpected dimensions
            return cos_phase

    SymmetryUtils.mirror_obs_sin_phase = mirror_obs_sin_phase  # type: ignore[attr-defined]
    SymmetryUtils.mirror_obs_cos_phase = mirror_obs_cos_phase  # type: ignore[attr-defined]

_patch_phase_mirroring()
patch_asset_path_resolution()

# Apply asset path resolution patches
from holosoma_ext.utils import patch_asset_path_resolution
patch_asset_path_resolution()
