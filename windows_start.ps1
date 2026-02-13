param([switch]$Hidden)

# Console colors
$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"
Write-Host "🚀 Program started" -ForegroundColor $GREEN

# Start program
Write-Host "Installing Python 3.14..." -ForegroundColor $GREEN
uv run main.py

Write-Host "✅ All done! Run: uv run python main.py" -ForegroundColor $GREEN

if ($Hidden) { exit } else { Read-Host "Press Enter to close" }
