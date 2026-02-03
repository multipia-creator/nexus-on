#!/bin/bash
# Contract Test Runner
# Run all contract tests locally

set -e

echo "🔒 NEXUS Contract Tests"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend Tests
echo "📦 Running Backend Contract Tests..."
echo "-------------------------------------"
cd backend

# Check if pytest is installed
if ! python -m pytest --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest not installed. Installing...${NC}"
    pip install -r requirements-dev.txt
fi

# Run backend tests
if python -m pytest tests/test_contracts.py -v --tb=short; then
    echo -e "${GREEN}✅ Backend contracts verified!${NC}"
    BACKEND_RESULT=0
else
    echo -e "${RED}❌ Backend contracts failed!${NC}"
    BACKEND_RESULT=1
fi

cd ..
echo ""

# Frontend Tests
echo "🌐 Running Frontend Contract Tests..."
echo "--------------------------------------"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing...${NC}"
    npm install
fi

# Check if vitest is installed
if ! npm list vitest &> /dev/null; then
    echo -e "${YELLOW}⚠️  vitest not installed. Installing...${NC}"
    npm install vitest --save-dev
fi

# Run frontend tests
if npm test; then
    echo -e "${GREEN}✅ Frontend contracts verified!${NC}"
    FRONTEND_RESULT=0
else
    echo -e "${RED}❌ Frontend contracts failed!${NC}"
    FRONTEND_RESULT=1
fi

cd ..
echo ""

# Summary
echo "🎯 Contract Test Summary"
echo "========================="
if [ $BACKEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Backend: PASS${NC}"
else
    echo -e "${RED}❌ Backend: FAIL${NC}"
fi

if [ $FRONTEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend: PASS${NC}"
else
    echo -e "${RED}❌ Frontend: FAIL${NC}"
fi

echo ""
echo "Verified Contracts:"
echo "  - AgentReport type (all required fields)"
echo "  - SSE StreamEvent format (snapshot/report/ping)"
echo "  - Device Pairing flow (start/confirm/complete)"
echo "  - Health endpoint (/health)"

# Exit with error if any test failed
if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ Some contract tests failed!${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}🔒 All contracts maintained!${NC}"
    exit 0
fi
