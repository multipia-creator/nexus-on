# NEXUS-ON Windows Engine Bootstrap Script
# Version: 1.0.0
# Purpose: Automated installation of NEXUS-ON engine on Windows 11

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\NEXUS-ON",
    [switch]$SkipPython = $false,
    [switch]$SkipGit = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEXUS-ON Windows Engine Installer" -ForegroundColor Cyan
Write-Host "  Version 1.0.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some features may require admin privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Check winget availability
Write-Host "🔍 Checking winget..." -ForegroundColor Green
$wingetPath = (Get-Command winget -ErrorAction SilentlyContinue).Source
if (-not $wingetPath) {
    Write-Host "❌ winget not found!" -ForegroundColor Red
    Write-Host "   Please install App Installer from Microsoft Store" -ForegroundColor Red
    Write-Host "   https://apps.microsoft.com/store/detail/9NBLGGH4NNS1" -ForegroundColor Cyan
    exit 1
}
Write-Host "✅ winget found: $wingetPath" -ForegroundColor Green
Write-Host ""

# Step 2: Install Python 3.10+ if needed
if (-not $SkipPython) {
    Write-Host "🐍 Checking Python..." -ForegroundColor Green
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[0-9]") {
        Write-Host "✅ Python already installed: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "📦 Installing Python 3.11..." -ForegroundColor Yellow
        winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Python installation failed" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Python installed successfully" -ForegroundColor Green
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
} else {
    Write-Host "⏭️  Skipping Python installation" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Install Git if needed
if (-not $SkipGit) {
    Write-Host "🔧 Checking Git..." -ForegroundColor Green
    $gitVersion = git --version 2>&1
    if ($gitVersion -match "git version") {
        Write-Host "✅ Git already installed: $gitVersion" -ForegroundColor Green
    } else {
        Write-Host "📦 Installing Git..." -ForegroundColor Yellow
        winget install Git.Git --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Git installation failed" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Git installed successfully" -ForegroundColor Green
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
} else {
    Write-Host "⏭️  Skipping Git installation" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Create installation directory
Write-Host "📁 Creating installation directory..." -ForegroundColor Green
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}
Write-Host "✅ Installation path: $InstallPath" -ForegroundColor Green
Write-Host ""

# Step 5: Download NEXUS-ON engine
Write-Host "📥 Downloading NEXUS-ON engine..." -ForegroundColor Green
$engineUrl = "https://nexus-3bm.pages.dev/downloads/windows/nexus-engine.zip"
$engineZip = Join-Path $InstallPath "nexus-engine.zip"

try {
    Invoke-WebRequest -Uri $engineUrl -OutFile $engineZip -UseBasicParsing
    Write-Host "✅ Engine downloaded successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Download failed: $_" -ForegroundColor Red
    Write-Host "   Falling back to GitHub release..." -ForegroundColor Yellow
    $githubUrl = "https://github.com/multipia-creator/nexus-on/releases/latest/download/nexus-engine-windows.zip"
    try {
        Invoke-WebRequest -Uri $githubUrl -OutFile $engineZip -UseBasicParsing
        Write-Host "✅ Engine downloaded from GitHub" -ForegroundColor Green
    } catch {
        Write-Host "❌ GitHub download also failed: $_" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Step 6: Extract engine
Write-Host "📦 Extracting engine..." -ForegroundColor Green
Expand-Archive -Path $engineZip -DestinationPath $InstallPath -Force
Remove-Item $engineZip
Write-Host "✅ Engine extracted successfully" -ForegroundColor Green
Write-Host ""

# Step 7: Install Python dependencies
Write-Host "📚 Installing Python dependencies..." -ForegroundColor Green
$requirementsPath = Join-Path $InstallPath "backend\requirements.txt"
if (Test-Path $requirementsPath) {
    python -m pip install --upgrade pip
    python -m pip install -r $requirementsPath
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements.txt not found, skipping..." -ForegroundColor Yellow
}
Write-Host ""

# Step 8: Create .env file if not exists
Write-Host "⚙️  Creating configuration..." -ForegroundColor Green
$envPath = Join-Path $InstallPath "backend\.env"
if (-not (Test-Path $envPath)) {
    $envExample = Join-Path $InstallPath "backend\.env.example"
    if (Test-Path $envExample) {
        Copy-Item $envExample $envPath
        Write-Host "✅ .env file created from template" -ForegroundColor Green
        Write-Host "   📝 Please edit $envPath with your API keys" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  .env.example not found" -ForegroundColor Yellow
    }
}
Write-Host ""

# Step 9: Create Windows Service (optional)
Write-Host "🔧 Would you like to install NEXUS-ON as a Windows Service?" -ForegroundColor Green
Write-Host "   This allows NEXUS-ON to run automatically at startup" -ForegroundColor Gray
$createService = Read-Host "Install as service? (Y/n)"
if ($createService -ne 'n' -and $createService -ne 'N') {
    Write-Host "📦 Creating Windows Service..." -ForegroundColor Green
    
    $serviceName = "NEXUS-ON-Engine"
    $serviceDisplayName = "NEXUS-ON AI Engine"
    $serviceDescription = "NEXUS-ON Local AI Character Assistant Engine"
    $servicePath = Join-Path $InstallPath "backend\start_server.py"
    $pythonExe = (Get-Command python).Source
    
    # Create NSSM service wrapper (if NSSM is available)
    $nssmPath = (Get-Command nssm -ErrorAction SilentlyContinue).Source
    if ($nssmPath) {
        nssm install $serviceName $pythonExe $servicePath
        nssm set $serviceName AppDirectory (Join-Path $InstallPath "backend")
        nssm set $serviceName DisplayName $serviceDisplayName
        nssm set $serviceName Description $serviceDescription
        nssm set $serviceName Start SERVICE_AUTO_START
        Write-Host "✅ Service created with NSSM" -ForegroundColor Green
    } else {
        Write-Host "⚠️  NSSM not found, creating scheduled task instead..." -ForegroundColor Yellow
        # Create scheduled task to run at startup
        $action = New-ScheduledTaskAction -Execute $pythonExe -Argument $servicePath -WorkingDirectory (Join-Path $InstallPath "backend")
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName $serviceName -Action $action -Trigger $trigger -Settings $settings -Description $serviceDescription -Force
        Write-Host "✅ Scheduled task created" -ForegroundColor Green
    }
}
Write-Host ""

# Step 10: Test installation
Write-Host "🧪 Testing installation..." -ForegroundColor Green
$testScript = Join-Path $InstallPath "backend\start_server.py"
if (Test-Path $testScript) {
    Write-Host "✅ Installation complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Next Steps:" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "1. Edit .env file with your API keys:" -ForegroundColor White
    Write-Host "   $envPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Start NEXUS-ON engine:" -ForegroundColor White
    Write-Host "   cd $InstallPath\backend" -ForegroundColor Gray
    Write-Host "   python start_server.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Access NEXUS-ON at:" -ForegroundColor White
    Write-Host "   http://localhost:7100" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Connect from web app:" -ForegroundColor White
    Write-Host "   https://nexus-3bm.pages.dev" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "❌ Installation verification failed" -ForegroundColor Red
    Write-Host "   start_server.py not found" -ForegroundColor Red
    exit 1
}

Write-Host "✨ Installation complete! Enjoy NEXUS-ON! ✨" -ForegroundColor Cyan
Write-Host ""
