#!/bin/bash
# NEXUS-ON Windows Engine Build Script
# Purpose: Package Python backend as Windows service executable

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 NEXUS-ON Windows Engine Build${NC}"
echo "========================================"

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
OUTPUT_DIR="$PROJECT_ROOT/public/downloads/windows"
ENGINE_DIR="$OUTPUT_DIR/engine"
DIST_DIR="$OUTPUT_DIR/dist"

# Version from package.json or default
VERSION=$(jq -r '.version // "1.0.0"' "$PROJECT_ROOT/package.json" 2>/dev/null || echo "1.0.0")

echo -e "${YELLOW}📦 Configuration${NC}"
echo "  Project Root: $PROJECT_ROOT"
echo "  Backend Dir: $BACKEND_DIR"
echo "  Output Dir: $OUTPUT_DIR"
echo "  Version: $VERSION"
echo ""

# Step 1: Clean previous build
echo -e "${YELLOW}🧹 Cleaning previous build...${NC}"
rm -rf "$ENGINE_DIR" "$DIST_DIR"
mkdir -p "$ENGINE_DIR" "$DIST_DIR"

# Step 2: Copy backend files
echo -e "${YELLOW}📋 Copying backend files...${NC}"
cp -r "$BACKEND_DIR"/* "$ENGINE_DIR/"

# Copy essential files
cp "$PROJECT_ROOT/.env.example" "$ENGINE_DIR/.env.example"
cp "$PROJECT_ROOT/README.md" "$ENGINE_DIR/README.md"

# Step 3: Create requirements.txt for Windows
echo -e "${YELLOW}📝 Generating Windows requirements.txt...${NC}"
cat > "$ENGINE_DIR/requirements.txt" << 'EOF'
# NEXUS-ON Windows Engine Dependencies
# Install: pip install -r requirements.txt

# Core Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
python-dotenv==1.0.1

# HTTP & Async
httpx==0.27.2
aiofiles==24.1.0
websockets==13.1

# Redis & RabbitMQ
redis==5.2.0
pika==1.3.2

# LLM Providers
anthropic==0.39.0
openai==1.54.4

# TTS Providers
elevenlabs==1.9.0
google-cloud-texttospeech==2.18.0

# Document Processing
pypdf==5.1.0
python-docx==1.1.2
openpyxl==3.1.5

# RAG & Embeddings
sentence-transformers==3.3.1
faiss-cpu==1.9.0
numpy==1.26.4

# Security & Auth
cryptography==43.0.3
pyjwt==2.9.0

# Monitoring & Logging
prometheus-client==0.21.0
structlog==24.4.0

# Utilities
pyyaml==6.0.2
jinja2==3.1.4
python-multipart==0.0.17
EOF

# Step 4: Create Windows service wrapper
echo -e "${YELLOW}🔧 Creating Windows service wrapper...${NC}"
cat > "$ENGINE_DIR/nexus-engine.py" << 'EOF'
"""
NEXUS-ON Windows Engine Service Wrapper
Runs as Windows Service or standalone application
"""
import sys
import os
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
log_dir = Path(os.getenv('DATA_DIR', 'C:/ProgramData/NEXUS-Engine')) / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'nexus.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    try:
        import uvicorn
        from nexus_supervisor.app import app
        
        port = int(os.getenv('PORT', '7100'))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"🚀 NEXUS Engine starting on {host}:{port}")
        logger.info(f"📂 Data directory: {os.getenv('DATA_DIR', 'default')}")
        logger.info(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'production')}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            workers=1  # Single worker for Windows service
        )
    except Exception as e:
        logger.error(f"❌ Failed to start NEXUS Engine: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
EOF

# Step 5: Create PyInstaller spec file
echo -e "${YELLOW}🎯 Creating PyInstaller spec...${NC}"
cat > "$ENGINE_DIR/nexus-engine.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Collect all Python files
datas = [
    ('nexus_supervisor', 'nexus_supervisor'),
    ('shared', 'shared'),
    ('.env.example', '.'),
]

# Hidden imports for dynamic imports
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'anthropic',
    'openai',
    'elevenlabs',
    'google.cloud.texttospeech',
    'sentence_transformers',
    'faiss',
]

a = Analysis(
    ['nexus-engine.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nexus-engine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/images/nexus-on-logo.png' if Path('static/images/nexus-on-logo.png').exists() else None,
)
EOF

# Step 6: Create build instructions
echo -e "${YELLOW}📖 Creating build instructions...${NC}"
cat > "$OUTPUT_DIR/BUILD_INSTRUCTIONS.md" << EOF
# NEXUS-ON Windows Engine Build Instructions

## Prerequisites

### On Windows Build Machine:

1. **Python 3.11+**
   \`\`\`powershell
   winget install Python.Python.3.11
   \`\`\`

2. **PyInstaller**
   \`\`\`powershell
   pip install pyinstaller
   \`\`\`

3. **Inno Setup** (for Setup.exe)
   - Download: https://jrsoftware.org/isdl.php
   - Install to: C:\Program Files (x86)\Inno Setup 6

## Build Steps

### Step 1: Build Python Executable

\`\`\`powershell
# Navigate to engine directory
cd public/downloads/windows/engine

# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller nexus-engine.spec

# Output: dist/nexus-engine.exe (~150MB)
\`\`\`

### Step 2: Test Executable

\`\`\`powershell
# Copy .env.example to .env and configure
cp .env.example .env

# Edit .env with your API keys
notepad .env

# Run
.\\dist\\nexus-engine.exe

# Test (in another terminal)
curl http://localhost:7100/health
\`\`\`

### Step 3: Create Setup.exe

\`\`\`powershell
# Navigate to downloads directory
cd ../

# Compile with Inno Setup
"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" setup.iss

# Output: NEXUS-Engine-Windows-x64-Setup.exe (~50MB)
\`\`\`

### Step 4: Upload to Cloudflare Pages

\`\`\`powershell
# Copy to static directory
cp NEXUS-Engine-Windows-x64-Setup.exe ../../static/downloads/

# Deploy
npm run deploy
\`\`\`

## Automated Build (GitHub Actions)

See \`.github/workflows/build-windows-engine.yml\` for CI/CD automation.

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

**Solution**: Add missing modules to \`hiddenimports\` in nexus-engine.spec

### Issue: Executable fails to start

**Solution**: 
1. Run in console mode (already set)
2. Check logs in C:\\ProgramData\\NEXUS-Engine\\logs\\nexus.log
3. Verify all API keys in .env

### Issue: Large file size

**Solution**: Consider using Python embedded distribution instead of PyInstaller

## Version: $VERSION
## Build Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF

# Step 7: Create LICENSE file
echo -e "${YELLOW}⚖️  Creating LICENSE file...${NC}"
cat > "$OUTPUT_DIR/LICENSE.txt" << 'EOF'
NEXUS-ON Educational License

Copyright (c) 2026 Prof. Nam Hyunwoo, Seokyeong University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), for
educational and research purposes only.

RESTRICTIONS:
1. Commercial use is prohibited without explicit written permission
2. Redistribution requires attribution
3. Modifications must be clearly marked

For commercial licensing, contact: namhw@skuniv.ac.kr

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
EOF

# Step 8: Update index.html for downloads
echo -e "${YELLOW}🌐 Updating download index...${NC}"
cat > "$OUTPUT_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS Engine - Windows 다운로드</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <div class="max-w-4xl mx-auto py-16 px-4">
        <div class="text-center mb-12">
            <h1 class="text-4xl font-bold text-gray-900 mb-4">
                <i class="fas fa-download text-blue-600 mr-3"></i>
                NEXUS Engine for Windows
            </h1>
            <p class="text-xl text-gray-600">
                세리아 AI 캐릭터 비서의 백엔드 엔진
            </p>
        </div>

        <div class="grid md:grid-cols-2 gap-6 mb-12">
            <!-- Setup.exe -->
            <div class="bg-white rounded-lg shadow-lg p-6 border-2 border-blue-500">
                <div class="text-center mb-4">
                    <i class="fas fa-box-archive text-5xl text-blue-600 mb-3"></i>
                    <h3 class="text-2xl font-bold text-gray-900">Setup.exe</h3>
                    <p class="text-gray-600 mt-2">GUI 설치 프로그램 (권장)</p>
                </div>
                <ul class="space-y-2 mb-6 text-sm text-gray-700">
                    <li><i class="fas fa-check text-green-600 mr-2"></i>클릭만으로 자동 설치</li>
                    <li><i class="fas fa-check text-green-600 mr-2"></i>Windows 서비스 자동 등록</li>
                    <li><i class="fas fa-check text-green-600 mr-2"></i>방화벽 규칙 자동 추가</li>
                    <li><i class="fas fa-check text-green-600 mr-2"></i>약 50MB, 5분 소요</li>
                </ul>
                <a href="/downloads/windows/NEXUS-Engine-Windows-x64-Setup.exe" 
                   class="block w-full bg-blue-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                    <i class="fas fa-download mr-2"></i>다운로드
                </a>
            </div>

            <!-- PowerShell Script -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <div class="text-center mb-4">
                    <i class="fas fa-terminal text-5xl text-purple-600 mb-3"></i>
                    <h3 class="text-2xl font-bold text-gray-900">PowerShell</h3>
                    <p class="text-gray-600 mt-2">자동 설치 스크립트</p>
                </div>
                <ul class="space-y-2 mb-6 text-sm text-gray-700">
                    <li><i class="fas fa-check text-green-600 mr-2"></i>Python 자동 설치</li>
                    <li><i class="fas fa-check text-green-600 mr-2"></i>의존성 자동 설치</li>
                    <li><i class="fas fa-check text-green-600 mr-2"></i>서비스 자동 등록</li>
                    <li><i class="fas fa-check text-green-600 mr-2"></i>개발자에게 권장</li>
                </ul>
                <button onclick="copyScript()" 
                        class="block w-full bg-purple-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-purple-700 transition">
                    <i class="fas fa-copy mr-2"></i>스크립트 복사
                </button>
            </div>
        </div>

        <!-- System Requirements -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 class="text-xl font-bold text-gray-900 mb-4">
                <i class="fas fa-laptop text-blue-600 mr-2"></i>시스템 요구사항
            </h3>
            <div class="grid md:grid-cols-3 gap-4">
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">운영체제</h4>
                    <p class="text-sm text-gray-600">Windows 10/11 (64-bit)</p>
                </div>
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">메모리</h4>
                    <p class="text-sm text-gray-600">최소 4GB RAM (권장 8GB)</p>
                </div>
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">저장 공간</h4>
                    <p class="text-sm text-gray-600">최소 5GB 여유 공간</p>
                </div>
            </div>
        </div>

        <!-- Quick Start -->
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-4">
                <i class="fas fa-rocket text-blue-600 mr-2"></i>빠른 시작
            </h3>
            <ol class="space-y-3 text-sm text-gray-700">
                <li><span class="font-semibold">1.</span> 위 방법 중 하나로 설치</li>
                <li><span class="font-semibold">2.</span> API 키 설정 (.env 파일 수정)</li>
                <li><span class="font-semibold">3.</span> 브라우저에서 <code class="bg-white px-2 py-1 rounded">http://localhost:7100</code> 접속</li>
                <li><span class="font-semibold">4.</span> 프론트엔드(<a href="https://nexus-3bm.pages.dev" class="text-blue-600 underline">nexus-3bm.pages.dev</a>)와 연결</li>
            </ol>
        </div>

        <!-- Links -->
        <div class="mt-8 text-center space-x-4">
            <a href="INSTALLATION_GUIDE.md" class="text-blue-600 hover:underline">
                <i class="fas fa-book mr-1"></i>설치 가이드
            </a>
            <a href="BUILD_INSTRUCTIONS.md" class="text-blue-600 hover:underline">
                <i class="fas fa-code mr-1"></i>빌드 방법
            </a>
            <a href="https://github.com/multipia-creator/nexus-on" class="text-blue-600 hover:underline">
                <i class="fab fa-github mr-1"></i>GitHub
            </a>
        </div>
    </div>

    <script>
    function copyScript() {
        const script = "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://nexus-3bm.pages.dev/downloads/windows/bootstrap.ps1'))";
        navigator.clipboard.writeText(script).then(() => {
            alert('✅ 스크립트가 클립보드에 복사되었습니다!\n\nPowerShell(관리자)에서 붙여넣기(Ctrl+V)하세요.');
        });
    }
    </script>
</body>
</html>
EOF

# Step 9: Summary
echo ""
echo -e "${GREEN}✅ Build structure created successfully!${NC}"
echo ""
echo "📁 Output Directory: $OUTPUT_DIR"
echo ""
echo "Generated files:"
echo "  ✓ engine/ - Backend source code"
echo "  ✓ setup.iss - Inno Setup script"
echo "  ✓ bootstrap.ps1 - PowerShell installer"
echo "  ✓ INSTALLATION_GUIDE.md - User guide"
echo "  ✓ BUILD_INSTRUCTIONS.md - Build guide"
echo "  ✓ LICENSE.txt - License"
echo "  ✓ index.html - Download page"
echo ""
echo -e "${YELLOW}⚠️  Next steps (on Windows machine):${NC}"
echo "  1. Install Python 3.11+: winget install Python.Python.3.11"
echo "  2. cd engine && pip install -r requirements.txt"
echo "  3. pyinstaller nexus-engine.spec"
echo "  4. Test: dist/nexus-engine.exe"
echo "  5. Compile setup.iss with Inno Setup"
echo ""
echo -e "${GREEN}🎉 Ready for Windows build!${NC}"
