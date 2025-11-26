"""Setup script for holosoma_inference_ext package."""

from setuptools import find_packages, setup

setup(
    name="holosoma_inference_ext",
    version="0.1.0",
    description="Holosoma Inference Extension - Go2 Quadruped Support",
    author="FAR Team",
    packages=find_packages(),
    package_data={
        "holosoma_inference_ext": [
            "py.typed",
            "config/**/*.yaml",
            "data/**/*.xml",
            "data/**/*.obj",
            "data/**/*.dae",
        ]
    },
    install_requires=[
        "holosoma_inference",
        "pyyaml",
    ],
    python_requires=">=3.8",
)
