#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

# 1. Check/install uv
if ! command -v uv &> /dev/null; then
    log "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.cargo/env
fi

# 2. Install Python 3.14
log "Installing Python 3.14..."
uv python install 3.14

# 3. Create/activate venv
log "Creating virtual environment..."
uv venv --python 314

# 4. Copy .env
if [[ ! -f .env ]]; then
    cp .env.example .env || warn ".env.example not found, create manually"
fi

# 5. Sync Python dependencies
log "Syncing Python packages (frozen)..."
uv sync --frozen

# 6. Check/install Homebrew (macOS only)
if [[ "$(uname -s)" == "Darwin" ]] && ! command -v brew &> /dev/null; then
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Добавляем в PATH (если нужно)
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# 7. Check/install ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    log "Installing ffmpeg..."
    if [[ "$(uname -s)" == "Darwin" ]]; then
        brew install ffmpeg || error "Install Homebrew: /bin/bash -c https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
    elif [[ "$(uname -s)" == "Linux" ]]; then
        sudo apt update && sudo apt install -y ffmpeg || error "Failed to install ffmpeg"
    else
        error "Unknown OS. Install ffmpeg manually"
    fi
fi

chmod +x macos_start.command

# 8. Create folders
mkdir -p bottom_videos result_videos source_videos temp

log "✅ All done! Run: uv run python main.py"
