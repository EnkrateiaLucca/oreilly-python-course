# O'Reilly Python Course - Setup Diagnostic Tool
# Run this if you're having issues to diagnose what's wrong

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Diagnostic Tool" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will check your setup and identify issues" -ForegroundColor Yellow
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Function to show check result
function Show-Check {
    param($name, $status, $details = "")
    if ($status) {
        Write-Host "✅ $name" -ForegroundColor Green
        if ($details) {
            Write-Host "   $details" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "❌ $name" -ForegroundColor Red
        if ($details) {
            Write-Host "   $details" -ForegroundColor Yellow
        }
    }
}

$issues = @()

# ============================================
# System Information
# ============================================
Write-Host "📊 System Information:" -ForegroundColor Cyan
Write-Host "   Windows Version: $([System.Environment]::OSVersion.Version)" -ForegroundColor Gray
Write-Host "   PowerShell Version: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
Write-Host "   Current Directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# ============================================
# Check Python
# ============================================
Write-Host "🐍 Python:" -ForegroundColor Cyan
if (Test-CommandExists "python") {
    $pythonVersion = python --version 2>&1
    $pythonPath = (Get-Command python).Source

    Show-Check "Python installed" $true "$pythonVersion"
    Write-Host "   Location: $pythonPath" -ForegroundColor Gray

    # Check version
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $majorVersion = [int]$matches[1]
        $minorVersion = [int]$matches[2]

        if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 13)) {
            Show-Check "Python version adequate (need 3.13+)" $false "Current: $majorVersion.$minorVersion"
            $issues += "Python version is too old. Need 3.13 or higher."
        }
        else {
            Show-Check "Python version adequate (need 3.13+)" $true "$majorVersion.$minorVersion"
        }
    }

    # Check pip
    if (Test-CommandExists "pip") {
        $pipVersion = pip --version 2>&1
        Show-Check "pip installed" $true
    }
    else {
        Show-Check "pip installed" $false
        $issues += "pip is not available"
    }
}
else {
    Show-Check "Python installed" $false "Not found in PATH"
    $issues += "Python is not installed or not in PATH. Install from https://www.python.org/"
}
Write-Host ""

# ============================================
# Check Git
# ============================================
Write-Host "📁 Git:" -ForegroundColor Cyan
if (Test-CommandExists "git") {
    $gitVersion = git --version 2>&1
    $gitPath = (Get-Command git).Source

    Show-Check "Git installed" $true "$gitVersion"
    Write-Host "   Location: $gitPath" -ForegroundColor Gray
}
else {
    Show-Check "Git installed" $false "Not found in PATH"
    $issues += "Git is not installed or not in PATH. Install from https://git-scm.com/"
}
Write-Host ""

# ============================================
# Check UV
# ============================================
Write-Host "📦 UV Package Manager:" -ForegroundColor Cyan
if (Test-CommandExists "uv") {
    $uvVersion = uv --version 2>&1
    $uvPath = (Get-Command uv).Source

    Show-Check "UV installed" $true "$uvVersion"
    Write-Host "   Location: $uvPath" -ForegroundColor Gray
}
else {
    Show-Check "UV installed" $false "Not found in PATH"
    $issues += "UV is not installed. See WINDOWS_SETUP.md - Step 3"

    # Check common UV locations
    $cargoPath = "$env:USERPROFILE\.cargo\bin\uv.exe"
    if (Test-Path $cargoPath) {
        Write-Host "   ⚠️  UV found at: $cargoPath" -ForegroundColor Yellow
        Write-Host "   ⚠️  But not in PATH. You need to add it to PATH or restart terminal." -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# Check Project Setup
# ============================================
Write-Host "🔧 Project Setup:" -ForegroundColor Cyan

# Check if in project directory
$isProjectDir = Test-Path "pyproject.toml"
Show-Check "In project directory" $isProjectDir
if (-not $isProjectDir) {
    $issues += "Not in project directory. Navigate to oreilly-python-course folder first."
}

# Check virtual environment
$venvExists = Test-Path ".venv"
Show-Check "Virtual environment exists" $venvExists
if (-not $venvExists) {
    $issues += "Virtual environment not created. Run: uv sync"
}
else {
    # Check if venv has packages
    $sitePackages = ".venv\Lib\site-packages"
    if (Test-Path $sitePackages) {
        $packageCount = (Get-ChildItem $sitePackages -Directory | Measure-Object).Count
        Show-Check "Packages installed in venv" ($packageCount -gt 10) "$packageCount directories"
        if ($packageCount -le 10) {
            $issues += "Virtual environment seems incomplete. Run: uv sync"
        }
    }
}

# Check Jupyter kernel
if (Test-CommandExists "jupyter") {
    $kernels = jupyter kernelspec list 2>&1 | Out-String
    $hasKernel = $kernels -match "oreilly-automate-py"
    Show-Check "Jupyter kernel installed" $hasKernel
    if (-not $hasKernel) {
        $issues += "Jupyter kernel not installed. Run: uv run ipython kernel install --user --env VIRTUAL_ENV `"`$PWD\.venv`" --name=oreilly-automate-py"
    }
}

# Check .env file
$envExists = Test-Path ".env"
Show-Check ".env file exists" $envExists
if (-not $envExists) {
    Write-Host "   ⚠️  You'll need to create .env from .env.example" -ForegroundColor Yellow
}
else {
    $envContent = Get-Content ".env" -Raw
    $hasPlaceholders = $envContent -match "your-actual-|your_api_key_here|<your"
    if ($hasPlaceholders) {
        Write-Host "   ⚠️  .env has placeholder values - add real API keys" -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================
# Check Network/Firewall
# ============================================
Write-Host "🌐 Network & Connectivity:" -ForegroundColor Cyan

# Test internet connection
try {
    $null = Invoke-WebRequest -Uri "https://www.google.com" -TimeoutSec 5 -ErrorAction Stop
    Show-Check "Internet connection" $true
}
catch {
    Show-Check "Internet connection" $false "Cannot reach internet"
    $issues += "No internet connection or firewall blocking"
}

# Test PyPI (Python package index)
try {
    $null = Invoke-WebRequest -Uri "https://pypi.org" -TimeoutSec 5 -ErrorAction Stop
    Show-Check "Can reach PyPI (pypi.org)" $true
}
catch {
    Show-Check "Can reach PyPI (pypi.org)" $false "Connection blocked"
    $issues += "Cannot reach pypi.org - firewall may be blocking Python packages"
}

# Test GitHub
try {
    $null = Invoke-WebRequest -Uri "https://github.com" -TimeoutSec 5 -ErrorAction Stop
    Show-Check "Can reach GitHub" $true
}
catch {
    Show-Check "Can reach GitHub" $false "Connection blocked"
    $issues += "Cannot reach GitHub - firewall may be blocking"
}

Write-Host ""

# ============================================
# Check Execution Policy
# ============================================
Write-Host "🔒 PowerShell Security:" -ForegroundColor Cyan
$executionPolicy = Get-ExecutionPolicy -Scope CurrentUser
Show-Check "Execution policy allows scripts" ($executionPolicy -ne "Restricted") "Current: $executionPolicy"
if ($executionPolicy -eq "Restricted") {
    $issues += "PowerShell execution policy is Restricted. Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
}
Write-Host ""

# ============================================
# Summary
# ============================================
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "🎉 No issues found! Your setup looks good." -ForegroundColor Green
    Write-Host ""
    Write-Host "If you're still having problems:" -ForegroundColor Yellow
    Write-Host "1. See WINDOWS_SETUP.md for detailed troubleshooting" -ForegroundColor White
    Write-Host "2. Try running: uv sync --reinstall" -ForegroundColor White
    Write-Host "3. Report at: github.com/EnkrateiaLucca/oreilly-python-course/issues" -ForegroundColor White
}
else {
    Write-Host "Found $($issues.Count) issue(s):" -ForegroundColor Red
    Write-Host ""
    for ($i = 0; $i -lt $issues.Count; $i++) {
        Write-Host "$($i + 1). $($issues[$i])" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "📚 See WINDOWS_SETUP.md for step-by-step fixes" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "💾 Save this output? Copy and paste into a text file if you need to share it for support." -ForegroundColor Gray
Write-Host ""
