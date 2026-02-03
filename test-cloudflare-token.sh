#!/bin/bash

# NEXUS - Cloudflare API 토큰 테스트 스크립트
# 새 토큰 발급 후 이 스크립트로 즉시 테스트

set -e

echo "🔐 Cloudflare API 토큰 테스트"
echo "================================"
echo ""

# 1. 토큰 입력 요청
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "❌ CLOUDFLARE_API_TOKEN 환경 변수가 설정되지 않았습니다."
    echo ""
    echo "사용법:"
    echo "  export CLOUDFLARE_API_TOKEN='새-토큰-여기-붙여넣기'"
    echo "  ./test-cloudflare-token.sh"
    exit 1
fi

echo "✅ 환경 변수 CLOUDFLARE_API_TOKEN 확인됨"
echo ""

# 2. Wrangler 설치 확인
echo "📦 Wrangler 설치 확인 중..."
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler가 설치되지 않았습니다."
    echo "설치: npm install -g wrangler"
    exit 1
fi

WRANGLER_VERSION=$(wrangler --version 2>&1 | head -1)
echo "✅ Wrangler 설치됨: $WRANGLER_VERSION"
echo ""

# 3. Wrangler 인증 테스트
echo "🔑 Wrangler 인증 테스트 중..."
if wrangler whoami 2>&1 | grep -q "logged in"; then
    echo "✅ Wrangler 인증 성공!"
    wrangler whoami
    echo ""
else
    echo "❌ Wrangler 인증 실패"
    echo "토큰 권한을 확인해주세요:"
    echo "  - Account: Cloudflare Pages - Edit"
    exit 1
fi

# 4. Cloudflare Pages 프로젝트 목록 확인
echo "📄 Cloudflare Pages 프로젝트 목록 확인 중..."
if wrangler pages project list 2>&1 | grep -q "nexus-frontend"; then
    echo "✅ nexus-frontend 프로젝트 확인됨"
    echo ""
else
    echo "⚠️  nexus-frontend 프로젝트를 찾을 수 없습니다."
    echo "프로젝트 목록:"
    wrangler pages project list
    echo ""
fi

# 5. 토큰 저장 권장
echo "💾 토큰 저장 권장사항"
echo "================================"
echo ""
echo "✅ 추천: .env.local 파일에 저장"
echo "  echo 'CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN' > /home/user/webapp/.env.local"
echo ""
echo "✅ 추천: ~/.bashrc에 추가 (영구 설정)"
echo "  echo 'export CLOUDFLARE_API_TOKEN=\"$CLOUDFLARE_API_TOKEN\"' >> ~/.bashrc"
echo "  source ~/.bashrc"
echo ""

# 6. 최종 결과
echo "🎉 모든 테스트 통과!"
echo "================================"
echo ""
echo "✅ 새 Cloudflare API 토큰이 정상적으로 작동합니다"
echo "✅ 이제 안전하게 배포할 수 있습니다"
echo ""
echo "배포 명령어:"
echo "  cd /home/user/webapp/frontend"
echo "  npm run build"
echo "  wrangler pages deploy dist --project-name nexus-frontend"
echo ""
