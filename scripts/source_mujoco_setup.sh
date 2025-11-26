# Detect script directory (works in both bash and zsh)
if [ -n "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
elif [ -n "${ZSH_VERSION}" ]; then
    SCRIPT_DIR=$( cd -- "$( dirname -- "${(%):-%x}" )" &> /dev/null && pwd )
fi
ROOT_DIR=$(dirname "$SCRIPT_DIR")
THIRDPARTY_DIR=$ROOT_DIR/thirdparty

# Source the holosoma setup
source $THIRDPARTY_DIR/holosoma/scripts/source_mujoco_setup.sh
