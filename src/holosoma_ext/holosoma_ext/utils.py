"""Utilities for @holosoma_ext/ path resolution."""
"""Keep this file in holosoma_ext at all times."""

import os
from pathlib import Path

_PATCH_STATE = {
    "isaacgym": False,
    "isaacsim": False,
    "mujoco": False,
    "inference": False,
    "training_export": False,
    "isaaclab_converter": False,
}


def _patch_once(key: str, fn) -> None:
    """Run a patch function once and record success state.

    Only skips if the patch was already successful (True).
    Failed patches (False) can be retried.
    """
    if _PATCH_STATE[key] is True:
        # Already successfully patched, skip
        return
    try:
        result = fn()
        _PATCH_STATE[key] = bool(result)
    except ImportError as e:
        # Allow environment without optional deps - can be retried later
        _PATCH_STATE[key] = False
    except Exception as e:
        _PATCH_STATE[key] = False


def _resolve_ext_path(path: str, ext_root: str) -> str:
    """Replace @holosoma_ext anywhere in path with the extension root."""
    token = "@holosoma_ext"
    if token not in path:
        return path

    # Keep the suffix after the token and join to ext_root for consistent absolute paths
    suffix = path.split(token, 1)[1]
    suffix = suffix.lstrip("/\\")
    return os.path.join(ext_root, suffix)


def resolve_robot_asset_paths(robot_config):
    """Return a robot_config with @holosoma_ext paths resolved if present."""
    from dataclasses import replace

    try:
        ext_root = os.path.dirname(os.path.abspath(__file__))
        asset = robot_config.asset
        resolved_root = _resolve_ext_path(asset.asset_root, ext_root)
        resolved_urdf = _resolve_ext_path(asset.urdf_file, ext_root)
        resolved_xml = _resolve_ext_path(asset.xml_file, ext_root) if asset.xml_file else asset.xml_file

        if (
            resolved_root != asset.asset_root
            or resolved_urdf != asset.urdf_file
            or resolved_xml != asset.xml_file
        ):
            new_asset = replace(asset, asset_root=resolved_root, urdf_file=resolved_urdf, xml_file=resolved_xml)
            return replace(robot_config, asset=new_asset)
    except Exception:
        pass
    return robot_config


def patch_asset_path_resolution():
    """Add @holosoma_ext/ path resolution to holosoma and holosoma_inference."""
    # Get ext_root from this file's location instead of importing holosoma_ext
    ext_root = os.path.dirname(os.path.abspath(__file__))

    def resolve_robot_configs():
        """Resolve @holosoma_ext in extension robot defaults upfront."""
        try:
            from dataclasses import replace

            from holosoma_ext.config_values import robot as ext_robot

            for name, cfg in list(ext_robot.DEFAULTS.items()):
                if not hasattr(cfg, "asset"):
                    continue
                asset = cfg.asset
                resolved_root = _resolve_ext_path(asset.asset_root, ext_root)
                resolved_urdf = _resolve_ext_path(asset.urdf_file, ext_root)
                resolved_xml = _resolve_ext_path(asset.xml_file, ext_root) if asset.xml_file else None
                if (
                    resolved_root != asset.asset_root
                    or resolved_urdf != asset.urdf_file
                    or resolved_xml != asset.xml_file
                ):
                    new_asset = replace(asset, asset_root=resolved_root, urdf_file=resolved_urdf, xml_file=resolved_xml)
                    ext_robot.DEFAULTS[name] = replace(cfg, asset=new_asset)
        except ImportError:
            pass

        try:
            from dataclasses import replace

            from holosoma_inference_ext.config_values import robot as inf_robot

            for name, cfg in list(inf_robot.DEFAULTS.items()):
                asset_root = getattr(cfg, "asset_root", None) or getattr(getattr(cfg, "asset", None), "asset_root", None)
                asset_file = getattr(cfg, "asset_file", None) or getattr(getattr(cfg, "asset", None), "asset_file", None)
                scene_xml = getattr(cfg, "robot_scene_xml", None)

                resolved_root = _resolve_ext_path(asset_root, ext_root) if asset_root else asset_root
                resolved_file = _resolve_ext_path(asset_file, ext_root) if asset_file else asset_file
                resolved_scene = _resolve_ext_path(scene_xml, ext_root) if scene_xml else scene_xml

                kwargs = {}
                updated = False
                if resolved_root and resolved_root != asset_root:
                    kwargs["asset_root"] = resolved_root
                    updated = True
                if resolved_file and resolved_file != asset_file:
                    kwargs["asset_file"] = resolved_file
                    updated = True
                if resolved_scene and resolved_scene != scene_xml:
                    kwargs["robot_scene_xml"] = resolved_scene
                    updated = True

                if updated:
                    inf_robot.DEFAULTS[name] = replace(cfg, **kwargs)
        except ImportError:
            pass

    resolve_robot_configs()

    def patch_isaacgym():
        from holosoma.simulator.isaacgym import isaacgym  # type: ignore[attr-defined]

        target_cls = getattr(isaacgym, "IsaacGymSimulator", None) or getattr(isaacgym, "IsaacGym", None)
        if target_cls is None:
            return False
        load_assets_fn = getattr(target_cls, "load_assets", None)
        if load_assets_fn is None or getattr(load_assets_fn, "_holosoma_ext_patched", False):
            return False

        def patched_load_assets(self):
            if self.robot_config.asset.asset_root.startswith("@holosoma_ext/"):
                from dataclasses import replace

                resolved_asset_root = _resolve_ext_path(self.robot_config.asset.asset_root, ext_root)
                new_asset = replace(self.robot_config.asset, asset_root=resolved_asset_root)
                self.robot_config = replace(self.robot_config, asset=new_asset)
            return load_assets_fn(self)

        patched_load_assets._holosoma_ext_patched = True  # type: ignore[attr-defined]
        setattr(target_cls, "load_assets", patched_load_assets)
        return True

    def patch_isaacsim():
        from holosoma.simulator.isaacsim import isaacsim

        target_cls = getattr(isaacsim, "IsaacSim", None)
        if target_cls is None:
            return False
        setup_scene_fn = getattr(target_cls, "_setup_scene", None)
        if setup_scene_fn is None:
            return False
        if getattr(setup_scene_fn, "_holosoma_ext_patched", False):
            return False

        def patched_setup_scene(self):
            # Resolve @holosoma_ext/ in asset_root and asset_file before calling original method
            from dataclasses import replace

            asset = self.robot_config.asset
            asset_root = asset.asset_root
            asset_file = asset.urdf_file

            resolved_asset_root = asset_root
            if asset_root.startswith("@holosoma_ext/") or "@holosoma_ext/" in asset_root:
                resolved_asset_root = _resolve_ext_path(asset_root, ext_root)

            resolved_asset_file = asset_file
            if asset_file.startswith("@holosoma_ext/") or "@holosoma_ext/" in asset_file:
                resolved_asset_file = _resolve_ext_path(asset_file, ext_root)

            if resolved_asset_root != asset_root or resolved_asset_file != asset_file:
                new_asset = replace(asset, asset_root=resolved_asset_root, urdf_file=resolved_asset_file)
                self.robot_config = replace(self.robot_config, asset=new_asset)
            return setup_scene_fn(self)

        patched_setup_scene._holosoma_ext_patched = True  # type: ignore[attr-defined]
        setattr(target_cls, "_setup_scene", patched_setup_scene)
        return True

    def patch_mujoco():
        from holosoma.simulator.mujoco import scene_manager

        add_robot_fn = scene_manager.MujocoSceneManager.add_robot
        if getattr(add_robot_fn, "_holosoma_ext_patched", False):
            return True

        def patched_add_robot(self, terrain_state, robot_config, xml_filter=None, prefix="robot_"):
            if robot_config.asset.asset_root.startswith("@holosoma_ext/"):
                from dataclasses import replace

                resolved_asset_root = _resolve_ext_path(robot_config.asset.asset_root, ext_root)
                new_asset = replace(robot_config.asset, asset_root=resolved_asset_root)
                robot_config = replace(robot_config, asset=new_asset)
            return add_robot_fn(self, terrain_state, robot_config, xml_filter, prefix)

        patched_add_robot._holosoma_ext_patched = True  # type: ignore[attr-defined]
        scene_manager.MujocoSceneManager.add_robot = patched_add_robot
        return True

    def patch_inference():
        from holosoma_inference.utils import misc

        resolve_fn = misc.resolve_holosoma_inference_path
        if getattr(resolve_fn, "_holosoma_ext_patched", False):
            return True

        def patched_resolve(path: str) -> str:
            if path.startswith("@holosoma_ext/"):
                return _resolve_ext_path(path, ext_root)
            return resolve_fn(path)

        patched_resolve._holosoma_ext_patched = True  # type: ignore[attr-defined]
        misc.resolve_holosoma_inference_path = patched_resolve
        return True

    def patch_training_export():
        from holosoma.utils import inference_helpers

        get_urdf_fn = inference_helpers.get_urdf_text_from_robot_config
        if getattr(get_urdf_fn, "_holosoma_ext_patched", False):
            return True

        def patched_get_urdf(robot_config):
            from dataclasses import replace

            asset_root = robot_config.asset.asset_root
            if asset_root.startswith("@holosoma_ext/"):
                resolved_asset_root = _resolve_ext_path(asset_root, ext_root)
                new_asset = replace(robot_config.asset, asset_root=resolved_asset_root)
                robot_config = replace(robot_config, asset=new_asset)
            return get_urdf_fn(robot_config)

        patched_get_urdf._holosoma_ext_patched = True  # type: ignore[attr-defined]
        inference_helpers.get_urdf_text_from_robot_config = patched_get_urdf
        return True

    def patch_isaaclab_converter():
        try:
            from isaaclab.sim.converters import asset_converter_base
        except ImportError:
            return False

        ctor = asset_converter_base.AssetConverterBase.__init__
        if getattr(ctor, "_holosoma_ext_patched", False):
            return True

        def patched_ctor(self, cfg):
            if hasattr(cfg, "asset_path") and isinstance(cfg.asset_path, str):
                if "@holosoma_ext/" in cfg.asset_path:
                    cfg.asset_path = _resolve_ext_path(cfg.asset_path, ext_root)
            return ctor(self, cfg)

        patched_ctor._holosoma_ext_patched = True  # type: ignore[attr-defined]
        asset_converter_base.AssetConverterBase.__init__ = patched_ctor  # type: ignore[assignment]
        return True

    _patch_once("isaacgym", patch_isaacgym)
    _patch_once("isaacsim", patch_isaacsim)
    _patch_once("mujoco", patch_mujoco)
    _patch_once("inference", patch_inference)
    _patch_once("training_export", patch_training_export)
    _patch_once("isaaclab_converter", patch_isaaclab_converter)
