# O'Reilly Python Course - Windows Setup Script
# This script automates the setup process and provides helpful error messages

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  O'Reilly Python Course - Windows Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Function to display error and exit
function Show-Error {
    param($message, $solution)
    Write-Host "❌ ERROR: $message" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 SOLUTION:" -ForegroundColor Yellow
    Write-Host $solution -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📚 For detailed troubleshooting, see WINDOWS_SETUP.md" -ForegroundColor Cyan
    exit 1
}

# Function to display success
function Show-Success {
    param($message)
    Write-Host "✅ $message" -ForegroundColor Green
}

# Function to display info
function Show-Info {
    param($message)
    Write-Host "ℹ️  $message" -ForegroundColor Blue
}

Write-Host "Starting setup checks..." -ForegroundColor Cyan
Write-Host ""

# ============================================
# Step 1: Check Python
# ============================================
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow

if (-not (Test-CommandExists "python")) {
    Show-Error "Python is not installed or not in PATH" @"
1. Download Python 3.13 from: https://www.python.org/downloads/
2. Run the installer and CHECK 'Add Python to PATH'
3. Restart this script after installation

See WINDOWS_SETUP.md - Step 1 for detailed instructions
"@
}

$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $majorVersion = [int]$matches[1]
    $minorVersion = [int]$matches[2]

    if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 13)) {
        Show-Error "Python version $majorVersion.$minorVersion is too old (need 3.13+)" @"
1. Download Python 3.13 from: https://www.python.org/downloads/
2. Install it (CHECK 'Add Python to PATH')
3. Restart this script

See WINDOWS_SETUP.md - Step 1 for detailed instructions
"@
    }
}

Show-Success "Python $pythonVersion is installed"
Write-Host ""

# ============================================
# Step 2: Check Git
# ============================================
Write-Host "🔍 Checking Git installation..." -ForegroundColor Yellow

if (-not (Test-CommandExists "git")) {
    Show-Error "Git is not installed or not in PATH" @"
1. Download Git from: https://git-scm.com/download/win
2. Run the installer (use default options)
3. Restart this script after installation

See WINDOWS_SETUP.md - Step 2 for detailed instructions
"@
}

$gitVersion = git --version 2>&1
Show-Success "Git is installed ($gitVersion)"
Write-Host ""

# ============================================
# Step 3: Check UV
# ============================================
Write-Host "🔍 Checking UV package manager..." -ForegroundColor Yellow

if (-not (Test-CommandExists "uv")) {
    Write-Host "⚠️  UV is not installed. Attempting to install..." -ForegroundColor Yellow
    Write-Host ""

    try {
        # Try to install UV
        Show-Info "Installing UV package manager..."
        Show-Info "This may trigger Windows Defender warnings - this is normal"
        Write-Host ""

        Invoke-Expression "& { $(Invoke-RestMethod https://astral.sh/uv/install.ps1) }"

        # Refresh PATH for current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

        if (-not (Test-CommandExists "uv")) {
            Show-Error "UV installation completed but UV is not in PATH" @"
1. Close this PowerShell window
2. Open a NEW PowerShell window
3. Run this script again

If problem persists, see WINDOWS_SETUP.md - Step 3 for manual installation
"@
        }

        Show-Success "UV installed successfully"
    }
    catch {
        Show-Error "Failed to install UV automatically" @"
Please install UV manually:

1. Open PowerShell as Administrator
2. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
3. Run: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
4. Close PowerShell and open a new one
5. Run this script again

See WINDOWS_SETUP.md - Step 3 for detailed instructions
"@
    }
}
else {
    $uvVersion = uv --version 2>&1
    Show-Success "UV is installed ($uvVersion)"
}
Write-Host ""

# ============================================
# Step 4: Sync Dependencies
# ============================================
Write-Host "📦 Installing Python packages..." -ForegroundColor Yellow
Show-Info "This will take 3-10 minutes depending on your internet speed"
Show-Info "You'll see lots of download/install messages - this is normal"
Write-Host ""

try {
    uv sync
    if ($LASTEXITCODE -ne 0) {
        throw "UV sync failed with exit code $LASTEXITCODE"
    }
    Show-Success "All packages installed successfully"
}
catch {
    Show-Error "Failed to install packages" @"
Common causes:
1. Slow/interrupted internet connection - try again
2. Antivirus blocking downloads - temporarily disable it
3. Corporate firewall - may need to use personal network

Try running manually: uv sync -v (verbose mode to see what's failing)

See WINDOWS_SETUP.md - 'UV Sync Taking Forever' for more help
"@
}
Write-Host ""

# ============================================
# Step 5: Install Jupyter Kernel
# ============================================
Write-Host "🔧 Installing Jupyter kernel..." -ForegroundColor Yellow

try {
    $venvPath = (Get-Location).Path + "\.venv"
    uv run ipython kernel install --user --env VIRTUAL_ENV $venvPath --name=oreilly-automate-py
    if ($LASTEXITCODE -ne 0) {
        throw "Kernel installation failed"
    }
    Show-Success "Jupyter kernel installed successfully"
}
catch {
    Show-Error "Failed to install Jupyter kernel" @"
Try running manually:
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD\.venv" --name=oreilly-automate-py

See WINDOWS_SETUP.md - Step 4.5 for more help
"@
}
Write-Host ""

# ============================================
# Step 6: Install Playwright
# ============================================
Write-Host "🌐 Installing Playwright browsers..." -ForegroundColor Yellow
Show-Info "This downloads ~500MB of browser files - may take 2-5 minutes"
Write-Host ""

try {
    uv run playwright install
    if ($LASTEXITCODE -ne 0) {
        # Non-fatal error - some students might not need browser automation
        Write-Host "⚠️  Playwright installation had issues (non-critical)" -ForegroundColor Yellow
        Write-Host "   You can install it later with: uv run playwright install" -ForegroundColor Yellow
    }
    else {
        Show-Success "Playwright browsers installed successfully"
    }
}
catch {
    Write-Host "⚠️  Playwright installation failed (non-critical)" -ForegroundColor Yellow
    Write-Host "   You can install it later with: uv run playwright install" -ForegroundColor Yellow
}
Write-Host ""

# ============================================
# Step 7: Check .env file
# ============================================
Write-Host "🔑 Checking API configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "1. Copy .env.example to .env" -ForegroundColor White
    Write-Host "2. Add your API keys:" -ForegroundColor White
    Write-Host "   - OpenAI: https://platform.openai.com/" -ForegroundColor White
    Write-Host "   - Anthropic: https://console.anthropic.com/" -ForegroundColor White
    Write-Host ""
    Write-Host "See WINDOWS_SETUP.md - Step 6 for detailed instructions" -ForegroundColor Cyan
}
else {
    Show-Success ".env file exists"

    # Check if keys are set (not just placeholders)
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "your-actual-|your_api_key_here|<your") {
        Write-Host "⚠️  .env file contains placeholder values" -ForegroundColor Yellow
        Write-Host "   Make sure to add your real API keys!" -ForegroundColor Yellow
    }
    else {
        Show-Success "API keys appear to be configured"
    }
}
Write-Host ""

# ============================================
# Setup Complete!
# ============================================
Write-Host "================================================" -ForegroundColor Green
Write-Host "  ✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start learning, run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   uv run --with jupyter jupyter lab" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Then navigate to: notebooks/01-python-fundamentals/" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 If you encounter any issues:" -ForegroundColor Cyan
Write-Host "   - See WINDOWS_SETUP.md for detailed troubleshooting" -ForegroundColor White
Write-Host "   - Report issues at: github.com/EnkrateiaLucca/oreilly-python-course/issues" -ForegroundColor White
Write-Host ""
Write-Host "Happy learning! 🎉" -ForegroundColor Green
Write-Host ""
