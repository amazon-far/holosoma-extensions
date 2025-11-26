"""Observation presets that incorporate extension-defined terms."""

from __future__ import annotations
from holosoma.config_types.termination import TerminationManagerCfg, TerminationTermCfg

from holosoma.config_values.termination import DEFAULTS as CORE_DEFAULTS

# GO2 12DOF Locomotion termination manager 

go2_12dof = TerminationManagerCfg(
    terms={
        "contact": TerminationTermCfg(
            func="holosoma.managers.termination.terms.locomotion:contact_forces_exceeded",
            params={
                "force_threshold": 1.0,
                "contact_indices_attr": "termination_contact_indices",
            },
        ),
        "timeout": TerminationTermCfg(
            func="holosoma.managers.termination.terms.common:timeout_exceeded",
            is_timeout=True,
        ),
    }
)

CORE_DEFAULTS.update(
    {
        "go2_12dof": go2_12dof
    }
)

DEFAULTS = CORE_DEFAULTS

__all__ = [
    "DEFAULTS",
    "go2_12dof",
]
