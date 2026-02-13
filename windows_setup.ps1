param([switch]$Hidden)

# Console colors
$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"
Write-Host "🚀 Project Setup" -ForegroundColor $GREEN

# 1. Install uv (Windows)
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..." -ForegroundColor $GREEN
    irm https://astral.sh/uv/install.ps1 | iex
    $env:PATH += ";$env:USERPROFILE\.cargo\bin"
    refreshenv  # Chocolatey or restart shell
}

# 2. Install Python 3.14
Write-Host "Installing Python 3.14..." -ForegroundColor $GREEN
uv python install 3.14

# 3. Create venv
Write-Host "Creating virtual environment..." -ForegroundColor $GREEN
uv venv --python 3.14

# 4. Copy .env
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
    if (-not (Test-Path .env)) {
        Write-Warning ".env.example not found, create manually"
    }
}

# 5. Sync dependencies
Write-Host "Syncing Python packages..." -ForegroundColor $GREEN
uv sync --frozen

# 6. Install ffmpeg (Windows)
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "Installing ffmpeg..." -ForegroundColor $GREEN

    # Download ffmpeg release
    $FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    $TEMP_ZIP = "$env:TEMP\ffmpeg.zip"
    $FFMPEG_DIR = "C:\ffmpeg"

    Invoke-WebRequest -Uri $FFMPEG_URL -OutFile $TEMP_ZIP
    Expand-Archive $TEMP_ZIP -DestinationPath $FFMPEG_DIR -Force
    Remove-Item $TEMP_ZIP

    # Add PATH
    $env:PATH += ";$FFMPEG_DIR\bin"
    [Environment]::SetEnvironmentVariable("PATH", $env:PATH, [EnvironmentVariableTarget]::User)

    Write-Host "FFmpeg installed to $FFMPEG_DIR" -ForegroundColor $GREEN
}

# 7. Create folders
New-Item -ItemType Directory -Force -Path "bottom_videos","result_videos","source_videos","temp" | Out-Null

Write-Host "✅ All done! Run: uv run python main.py" -ForegroundColor $GREEN

if ($Hidden) { exit } else { Read-Host "Press Enter to close" }
