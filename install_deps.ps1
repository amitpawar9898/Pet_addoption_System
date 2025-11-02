# install_deps.ps1
# Activates .venv if available and installs requirements from requirements.txt
# Run from project root in PowerShell. Run as normal user (no admin required for venv installs).

$venvPath = Join-Path $PSScriptRoot '.venv\Scripts\Activate.ps1'
$requirements = Join-Path $PSScriptRoot 'requirements.txt'

if (Test-Path $venvPath) {
    Write-Host "Activating virtualenv..."
    & $venvPath
} else {
    Write-Host ".venv not found - creating one..."
    python -m venv .venv
    & $venvPath
}

Write-Host "Installing Python dependencies from requirements.txt..."
if (Test-Path $requirements) {
    pip install -r $requirements
} else {
    Write-Host "requirements.txt not found. Installing core packages..."
    pip install Flask-SQLAlchemy SQLAlchemy pymysql python-dotenv
}

Write-Host "Done. You can now run: python app.py"