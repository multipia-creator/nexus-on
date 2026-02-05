# NEXUS-ON Windows Engine Build Instructions

## Prerequisites

### On Windows Build Machine:

1. **Python 3.11+**
   ```powershell
   winget install Python.Python.3.11
   ```

2. **PyInstaller**
   ```powershell
   pip install pyinstaller
   ```

3. **Inno Setup** (for Setup.exe)
   - Download: https://jrsoftware.org/isdl.php
   - Install to: C:\Program Files (x86)\Inno Setup 6

## Build Steps

### Step 1: Build Python Executable

```powershell
# Navigate to engine directory
cd public/downloads/windows/engine

# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller nexus-engine.spec

# Output: dist/nexus-engine.exe (~150MB)
```

### Step 2: Test Executable

```powershell
# Copy .env.example to .env and configure
cp .env.example .env

# Edit .env with your API keys
notepad .env

# Run
.\dist\nexus-engine.exe

# Test (in another terminal)
curl http://localhost:7100/health
```

### Step 3: Create Setup.exe

```powershell
# Navigate to downloads directory
cd ../

# Compile with Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss

# Output: NEXUS-Engine-Windows-x64-Setup.exe (~50MB)
```

### Step 4: Upload to Cloudflare Pages

```powershell
# Copy to static directory
cp NEXUS-Engine-Windows-x64-Setup.exe ../../static/downloads/

# Deploy
npm run deploy
```

## Automated Build (GitHub Actions)

See `.github/workflows/build-windows-engine.yml` for CI/CD automation.

## Size Optimization

Current sizes:
- nexus-engine.exe: ~150MB (PyInstaller bundle)
- Setup.exe: ~50MB (Inno Setup installer)

To reduce size:
1. Remove unused dependencies from requirements.txt
2. Use UPX compression (already enabled)
3. Exclude test files and examples

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Add missing modules to `hiddenimports` in nexus-engine.spec

### Issue: Executable fails to start

**Solution**: 
1. Run in console mode (already set)
2. Check logs in C:\ProgramData\NEXUS-Engine\logs\nexus.log
3. Verify all API keys in .env

### Issue: Large file size

**Solution**: Consider using Python embedded distribution instead of PyInstaller

## Version: 1.0.0
## Build Date: 2026-02-05 07:12:40 UTC
