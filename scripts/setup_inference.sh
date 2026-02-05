#!/bin/bash
# Exit on error, and print commands
set -ex

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$(dirname "$SCRIPT_DIR")
THIRDPARTY_DIR=$ROOT_DIR/thirdparty

# Check if holosoma submodule is present, if not initialize it
if [ ! -d "$THIRDPARTY_DIR/holosoma" ] || [ -z "$(ls -A $THIRDPARTY_DIR/holosoma)" ]; then
    echo "Holosoma submodule not found. Initializing submodule..."
    cd $ROOT_DIR
    git submodule update --init --recursive thirdparty/holosoma
fi

# Run the holosoma setup script
cd $THIRDPARTY_DIR/holosoma
bash scripts/setup_inference.sh

# Source the holosoma common script to get conda environment variables
source $THIRDPARTY_DIR/holosoma/scripts/source_common.sh

# Activate the conda environment and install holosoma, holosoma_inference, and holosoma_inference_ext packages
source $CONDA_ROOT/bin/activate hsinference
cd $THIRDPARTY_DIR/holosoma/src/holosoma
pip install -e .
cd $THIRDPARTY_DIR/holosoma/src/holosoma_inference
pip install -e .
cd $ROOT_DIR/src/holosoma_inference_ext
pip install -e .
cd $ROOT_DIR/src/holosoma_ext
pip install -e .
