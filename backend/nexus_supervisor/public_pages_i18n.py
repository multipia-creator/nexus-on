"""
Public pages with i18n support (Korean/English toggle).
WORLD-CLASS AI Character Assistant Service.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("nexus_supervisor")

# Path to data directory
DATA_DIR = Path(__file__).parent.parent / "data"


def load_modules_data() -> List[Dict[str, Any]]:
    """Load modules.json data."""
    try:
        with open(DATA_DIR / "modules.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load modules.json: {e}")
        return []


def load_benchmark_data() -> List[Dict[str, Any]]:
    """Load benchmark.json data."""
    try:
        with open(DATA_DIR / "benchmark.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load benchmark.json: {e}")
        return []


# i18n Translations
TRANSLATIONS = {
    "ko": {
        "nav_home": "홈",
        "hero_input_placeholder": "무엇을 도와드릴까요?",
        "hero_voice_button": "음성 입력",
        "hero_text_button": "전송",
        "voice_not_supported": "이 브라우저는 음성 인식을 지원하지 않습니다.",
        
        "nav_intro": "소개",
        "nav_modules": "모듈",
        "nav_pricing": "가격",
        "nav_dashboard": "대시보드",
        "nav_canvas": "캔버스",
        "nav_login": "로그인",
        
        "hero_title": "잠들지 않는<br>당신만의 AI 캐릭터 비서",
        "hero_subtitle": "항상 깨어있는 당신만의 AI 캐릭터 비서",
        "hero_tagline": "Live2D 캐릭터가 화면에 항상 존재하며, 자율적으로 작업을 수행하지만<br>중요한 결정은 항상 당신의 승인을 받습니다.",
        "hero_cta_primary": "무료로 시작하기",
        "hero_cta_secondary": "데모 보기",
        
        "value1_title": "항상 화면에 존재",
        "value1_desc": "화면에 항상 존재하는 Live2D 캐릭터 비서.<br>5가지 상태로 현재 작업을 시각적으로 표현합니다.",
        "value2_title": "자율적이지만 통제 가능",
        "value2_desc": "자율적으로 작업을 수행하지만,<br>중요한 결정은 항상 당신의 승인을 받습니다.",
        "value3_title": "한국어 네이티브",
        "value3_desc": "한국어 네이티브 지원.<br>HWP 파일을 완벽하게 처리합니다.",
        
        "footer_text": "잠들지 않는 당신만의 AI 캐릭터 비서",
        "footer_dev": "개발: 남현우 교수, 서경대학교 VD_비주얼디자인전공",
        
        "pricing_title": "가격 플랜",
        "pricing_subtitle": "당신의 필요에 맞는 플랜을 선택하세요.<br>언제든지 업그레이드 가능합니다.",
        "pricing_coming": "가격 플랜 페이지 구현 중...",
        "pricing_plans": "FREE / PRO / ENTERPRISE 플랜 제공 예정",
        
        "dashboard_title": "대시보드 프리뷰",
        "dashboard_subtitle": "실시간으로 업데이트되는 AI 비서의 작업 현황을 확인하세요.",
        "dashboard_coming": "대시보드 프리뷰 페이지 구현 중...",
        "dashboard_features": "3-Column Layout | 실시간 SSE 업데이트 | Live2D 상태 변화",
        
        "canvas_title": "캔버스 워크스페이스",
        "canvas_subtitle": "AI 비서와 함께 문서를 작성하고 편집하세요.",
        "canvas_coming": "캔버스 워크스페이스 페이지 구현 중...",
        "canvas_features": "Markdown Editor | AI 제안 | Multi-format Export",
        
        "login_title": "다시 오신 것을 환영합니다",
        "login_subtitle": "다시 만나서 반가워요!",
        "login_email": "이메일",
        "login_password": "비밀번호",
        "login_button": "로그인",
        "login_no_account": "계정이 없으신가요?",
        "login_signup": "회원가입",
        
        "intro_title": "NEXUS-ON 소개",
        "intro_subtitle": "Live2D 캐릭터 비서 기반의 자율 AI 에이전트 시스템",
        "intro_section1_title": "핵심 개념",
        "intro_section1_content": "NEXUS-ON은 Live2D 캐릭터가 화면에 항상 존재하며, 자율적으로 작업을 수행하지만 중요한 결정은 항상 사용자의 승인을 받는 혁신적인 AI 비서 시스템입니다.",
        "intro_section2_title": "차별화 포인트",
        "intro_diff1": "시각적 존재감: 항상 화면에 존재하는 Live2D 캐릭터",
        "intro_diff2": "통제된 자율성: 자율적이지만 중요 결정은 승인 필요",
        "intro_diff3": "한국어 최적화: HWP 파일 네이티브 지원",
        "intro_diff4": "로컬 우선: 클라우드 업로드 없는 안전한 데이터 처리",
        
        "modules_title": "모듈 시스템",
        "modules_subtitle": "8개의 핵심 모듈로 구성된 강력한 AI 에이전트",
        "modules_count": "개 모듈",
        
        # Intro Page - World-class differentiators
        "intro_worldclass_title": "세계 최고 수준의 AI 비서",
        "intro_worldclass_subtitle": "NEXUS-ON이 다른 AI 비서와 차별화되는 이유",
        "intro_feature1_title": "🎭 Live2D 캐릭터 비서",
        "intro_feature1_content": "단순한 챗봇이 아닙니다. 화면에 항상 존재하는 Live2D 캐릭터가 5가지 상태(Idle, Listening, Thinking, Speaking, Busy)로 현재 작업을 시각적으로 표현합니다. Haru 모델 기반으로 실시간 애니메이션과 립싱크를 지원합니다.",
        "intro_feature2_title": "🛡️ Human-in-the-loop 승인 시스템",
        "intro_feature2_content": "ShieldCheck 시스템이 모든 작업을 위험도에 따라 GREEN/YELLOW/RED로 분류합니다. 파일 삭제나 외부 공유 같은 위험한 작업은 반드시 사용자 승인이 필요하며, Two-phase commit 프로토콜로 안전성을 보장합니다.",
        "intro_feature3_title": "📚 한국어 네이티브 지원",
        "intro_feature3_content": "HWP(한글 파일)을 외부 변환 없이 직접 처리하는 FileSearch 엔진을 탑재했습니다. Token overlap 기반 RAG로 한국어 학술 워크플로우에 최적화되어 있으며, 매일 03:00 KST에 자동으로 문서를 색인합니다.",
        "intro_feature4_title": "🔄 멀티 에이전트 오케스트레이션",
        "intro_feature4_content": "8개의 전문화된 모듈(Bot, ShieldCheck, FileSearch, Youtube, FileEdit, Users, MonitorCheck, Activity)이 협업하여 복잡한 작업을 자동으로 수행합니다. Claude Sonnet 4.5 기반으로 멀티스텝 작업을 지능적으로 처리합니다.",
        "intro_feature5_title": "🏠 Local-first 아키텍처",
        "intro_feature5_content": "모든 데이터는 로컬에서 처리되며 클라우드 업로드 없이 안전합니다. Multi-tenant 지원으로 조직 단위 배포가 가능하며, org-id 및 project-id 기반 격리로 데이터 유출을 원천 차단합니다.",
        "intro_feature6_title": "🎯 실시간 작업 모니터링",
        "intro_feature6_content": "SSE(Server-Sent Events)를 통해 세리아의 모든 행동을 실시간으로 추적합니다. Live2D 캐릭터가 작업 상태를 즉시 반영하며, RED 작업 시 Alert glow(빨간 테두리)로 승인 대기를 시각화합니다.",
        
        # Modules Page - Individual modules
        "module_bot_title": "Bot",
        "module_bot_subtitle": "Character Assistant Core",
        "module_bot_desc": "Live2D 캐릭터 + Claude Sonnet 4.5 대화형 에이전트. NEXUS의 심장부로, 4가지 애니메이션 상태를 통해 시각적 피드백을 제공하며 멀티턴 컨텍스트를 유지합니다.",
        "module_bot_status": "Production Ready",
        
        "module_shield_title": "ShieldCheck",
        "module_shield_subtitle": "Human-in-the-loop Approval System",
        "module_shield_desc": "위험 기반 승인 워크플로우 (GREEN/YELLOW/RED). 자동 실행, 알림, 명시적 승인의 3단계 게이트로 NEXUS가 무분별하게 행동하지 않도록 보호합니다.",
        "module_shield_status": "Production Ready",
        
        "module_filesearch_title": "FileSearch",
        "module_filesearch_subtitle": "RAG Engine (Token Overlap)",
        "module_filesearch_desc": "Token overlap 기반 검색으로 한국어 HWP 네이티브 지원. RAG 엔진은 한국어 학술 워크플로우에 최적화되어 있으며, 매일 03:00 KST 자동 색인으로 증거 추적이 가능합니다.",
        "module_filesearch_status": "Beta - Active Development",
        
        "module_youtube_title": "Youtube",
        "module_youtube_subtitle": "YouTube Integration",
        "module_youtube_desc": "연구 및 학습 워크플로우를 위한 완전한 YouTube 통합. YouTube Data API v3로 검색, 큐 관리, 내장 플레이어를 지원하며 Live2D 캐릭터가 Speaking 상태로 비디오 콘텐츠를 설명합니다.",
        "module_youtube_status": "Production Ready",
        
        "module_fileedit_title": "FileEdit",
        "module_fileedit_subtitle": "Canvas Workspace",
        "module_fileedit_desc": "멀티포맷 내보내기를 지원하는 협업 워크스페이스. 로컬 draft 저장소(서버 업로드 없음)로 문서를 작성하고 편집하며, Live2D 캐릭터가 Thinking 상태로 긴 draft 작업 시 표시됩니다.",
        "module_fileedit_status": "Beta - Under Refinement",
        
        "module_users_title": "Users",
        "module_users_subtitle": "Multi-tenant Context",
        "module_users_desc": "팀 배포를 위한 엔터프라이즈급 멀티테넌시. org-id 및 project-id로 범위를 지정하며, 테넌트별 API 키로 자격 증명을 격리합니다. 비용 태깅과 감사 추적으로 완전한 책임성을 보장합니다.",
        "module_users_status": "Production Ready",
        
        "module_monitor_title": "MonitorCheck",
        "module_monitor_subtitle": "Windows Agent",
        "module_monitor_desc": "Windows 환경 모니터링 에이전트 (베타). 시스템 상태를 추적하고 Live2D 캐릭터와 통합하여 시스템 이벤트를 실시간으로 보고합니다.",
        "module_monitor_status": "Beta - Windows Agent",
        
        "module_activity_title": "Activity",
        "module_activity_subtitle": "Activity Metrics",
        "module_activity_desc": "알파 단계의 활동 메트릭 추적 시스템. 세리아의 모든 행동을 로깅하고 분석하여 사용 패턴과 효율성을 측정합니다.",
        "module_activity_status": "Alpha - Metrics Only",
        
        # Pricing Page
        "pricing_free_title": "FREE",
        "pricing_free_price": "₩0",
        "pricing_free_period": "영원히 무료",
        "pricing_free_desc": "개인 사용자를 위한 기본 기능",
        "pricing_free_feature1": "✅ Live2D 캐릭터 비서 (Haru 모델)",
        "pricing_free_feature2": "✅ 기본 대화 (Claude Sonnet 4)",
        "pricing_free_feature3": "✅ 로컬 파일 처리 (최대 100개)",
        "pricing_free_feature4": "✅ ShieldCheck 승인 시스템",
        "pricing_free_feature5": "✅ 한국어/영어 지원",
        "pricing_free_feature6": "❌ 고급 모듈 (Youtube, FileSearch)",
        "pricing_free_feature7": "❌ 팀 협업 기능",
        "pricing_free_feature8": "❌ API 접근",
        
        "pricing_plus_title": "PLUS",
        "pricing_plus_price": "₩29,000",
        "pricing_plus_period": "/월",
        "pricing_plus_desc": "전문가를 위한 고급 기능",
        "pricing_plus_badge": "인기",
        "pricing_plus_feature1": "✅ FREE의 모든 기능",
        "pricing_plus_feature2": "✅ Claude Sonnet 4.5 (최신 모델)",
        "pricing_plus_feature3": "✅ 모든 8개 모듈 사용 가능",
        "pricing_plus_feature4": "✅ FileSearch RAG 엔진 (무제한)",
        "pricing_plus_feature5": "✅ Youtube 통합 (1시간 캐싱)",
        "pricing_plus_feature6": "✅ Canvas 워크스페이스 (무제한)",
        "pricing_plus_feature7": "✅ 우선 지원 (24시간 응답)",
        "pricing_plus_feature8": "❌ 팀 멀티테넌시",
        
        "pricing_pro_title": "PRO",
        "pricing_pro_price": "₩99,000",
        "pricing_pro_period": "/월",
        "pricing_pro_desc": "조직을 위한 엔터프라이즈 솔루션",
        "pricing_pro_badge": "추천",
        "pricing_pro_feature1": "✅ PLUS의 모든 기능",
        "pricing_pro_feature2": "✅ Multi-tenant 지원 (무제한 org/project)",
        "pricing_pro_feature3": "✅ 팀 협업 (최대 50명)",
        "pricing_pro_feature4": "✅ API 접근 (REST + SSE)",
        "pricing_pro_feature5": "✅ 커스텀 Live2D 모델 지원",
        "pricing_pro_feature6": "✅ 전용 서버 인스턴스",
        "pricing_pro_feature7": "✅ 감사 로그 및 비용 태깅",
        "pricing_pro_feature8": "✅ VIP 지원 (1시간 응답)",
        
        # Developer Profile Section
        "developer_title": "개발자 소개",
        "developer_name": "남현우 교수",
        "developer_affiliation": "서경대학교 디자인학부 VD_비주얼디자인전공 콘텐츠시스템",
        "developer_specialty": "AI, Blockchain, IoT, XR",
        "developer_website": "DXPIA.com",
        "developer_research_title": "연구 분야",
        "developer_research_1": "ICT 전략 & 콘텐츠 시스템 디자인",
        "developer_research_2": "AI 에이전트 시스템 및 Human-in-the-loop 인터페이스",
        "developer_research_3": "Blockchain 기반 ART NFT 플랫폼",
        "developer_research_4": "IoT 기반 뷰티 AI 서비스 시스템",
        "developer_research_5": "XR(VR/AR/MR) 및 메타버스 콘텐츠 전략",
        "developer_vision_title": "프로젝트 비전",
        "developer_vision_content": "NEXUS-ON은 인간-AI 협업의 새로운 패러다임을 제시합니다. Local-first 아키텍처로 데이터 안전을 보장하고, HWP를 포함한 한국어 문서를 완벽하게 처리하며, 항상 사용자의 통제 하에서 작동하는 투명하고 신뢰할 수 있는 AI 비서를 목표로 합니다.",
        "developer_philosophy_title": "개발 철학",
        "developer_philosophy_1": "Local-first: 클라우드 업로드 없는 안전한 데이터 처리",
        "developer_philosophy_2": "Human oversight: 중요한 결정은 항상 사용자 승인",
        "developer_philosophy_3": "Fail-safe: 오류 발생 시 안전한 기본 상태로 복귀",
        "developer_philosophy_4": "Open by design: 교육 및 연구를 위한 오픈소스 프로젝트",
        "developer_contact_title": "연락처",
        "developer_contact_dept": "서경대학교 디자인학부 VD_비주얼디자인전공",
        "developer_contact_lab": "콘텐츠시스템 Lab (AI, Blockchain, IoT, XR)",
        "developer_contact_website": "DXPIA.com",
        "developer_contact_project": "NEXUS-ON 오픈소스 프로젝트",
    },
    "en": {
        "nav_home": "Home",
        "nav_intro": "About",
        "nav_modules": "Modules",
        "nav_pricing": "Pricing",
        "nav_dashboard": "Dashboard",
        "nav_canvas": "Canvas",
        "nav_login": "Login",
        
        "hero_input_placeholder": "What can I help you with?",
        "hero_voice_button": "Voice Input",
        "hero_text_button": "Send",
        "voice_not_supported": "Your browser does not support speech recognition.",
        
        "hero_title": "Your AI Character Assistant<br>That Never Sleeps",
        "hero_subtitle": "Your Always-On AI Character Assistant",
        "hero_tagline": "A Live2D character is always present on your screen, working autonomously<br>but always seeking your approval for important decisions.",
        "hero_cta_primary": "Start Free",
        "hero_cta_secondary": "Watch Demo",
        
        "value1_title": "Always Visible",
        "value1_desc": "A Live2D character assistant always present on screen.<br>5 states visually represent current tasks.",
        "value2_title": "Autonomous but Controlled",
        "value2_desc": "Works autonomously,<br>but always requires your approval for critical decisions.",
        "value3_title": "Korean Native",
        "value3_desc": "Native Korean language support.<br>Handles HWP files perfectly.",
        
        "footer_text": "Your AI Character Assistant That Never Sleeps",
        "footer_dev": "Developed by Prof. Nam Hyunwoo, Seokyeong University VD_Visual Design",
        
        "pricing_title": "Pricing Plans",
        "pricing_subtitle": "Choose the plan that fits your needs.<br>Upgrade anytime.",
        "pricing_coming": "Pricing page under construction...",
        "pricing_plans": "FREE / PRO / ENTERPRISE plans coming soon",
        
        "dashboard_title": "Dashboard Preview",
        "dashboard_subtitle": "Monitor your AI assistant's real-time activity.",
        "dashboard_coming": "Dashboard preview page under construction...",
        "dashboard_features": "3-Column Layout | Real-time SSE Updates | Live2D State Changes",
        
        "canvas_title": "Canvas Workspace",
        "canvas_subtitle": "Create and edit documents with your AI assistant.",
        "canvas_coming": "Canvas workspace page under construction...",
        "canvas_features": "Markdown Editor | AI Suggestions | Multi-format Export",
        
        "login_title": "Welcome Back",
        "login_subtitle": "Good to see you again!",
        "login_email": "Email",
        "login_password": "Password",
        "login_button": "Sign In",
        "login_no_account": "Don't have an account?",
        "login_signup": "Sign Up",
        "login_google": "Sign in with Google",
        
        # Intro Page - World-class differentiators
        "intro_worldclass_title": "World-Class AI Assistant",
        "intro_worldclass_subtitle": "What makes NEXUS-ON different from other AI assistants",
        "intro_feature1_title": "🎭 Live2D Character Assistant",
        "intro_feature1_content": "Not just a chatbot. A Live2D character always present on screen displays current tasks through 5 states (Idle, Listening, Thinking, Speaking, Busy). Based on Haru model with real-time animation and lip-sync support.",
        "intro_feature2_title": "🛡️ Human-in-the-loop Approval System",
        "intro_feature2_content": "ShieldCheck system classifies all tasks by risk level: GREEN/YELLOW/RED. Dangerous operations like file deletion or external sharing require user approval, with Two-phase commit protocol ensuring safety.",
        "intro_feature3_title": "📚 Native Korean Support",
        "intro_feature3_content": "FileSearch engine processes HWP (Hangul files) directly without external conversion. Token overlap-based RAG optimized for Korean academic workflows, with automatic indexing at 03:00 KST daily.",
        "intro_feature4_title": "🔄 Multi-Agent Orchestration",
        "intro_feature4_content": "8 specialized modules (Bot, ShieldCheck, FileSearch, Youtube, FileEdit, Users, MonitorCheck, Activity) collaborate to automatically handle complex tasks. Claude Sonnet 4.5-based intelligent multi-step processing.",
        "intro_feature5_title": "🏠 Local-first Architecture",
        "intro_feature5_content": "All data processed locally, safe without cloud uploads. Multi-tenant support enables organization-wide deployment, with org-id and project-id-based isolation preventing data leaks.",
        "intro_feature6_title": "🎯 Real-time Task Monitoring",
        "intro_feature6_content": "Track all of Ceria's actions in real-time via SSE (Server-Sent Events). Live2D character immediately reflects task status, with Alert glow (red border) visualizing approval pending for RED tasks.",
        
        # Modules Page - Individual modules
        "module_bot_title": "Bot",
        "module_bot_subtitle": "Character Assistant Core",
        "module_bot_desc": "Live2D character + Claude Sonnet 4.5 conversational agent. Heart of NEXUS providing visual feedback through 4 animation states while maintaining multi-turn context.",
        "module_bot_status": "Production Ready",
        
        "module_shield_title": "ShieldCheck",
        "module_shield_subtitle": "Human-in-the-loop Approval System",
        "module_shield_desc": "Risk-based approval workflow (GREEN/YELLOW/RED). 3-tier gates of auto-execute, notify, and explicit approval protect NEXUS from reckless actions.",
        "module_shield_status": "Production Ready",
        
        "module_filesearch_title": "FileSearch",
        "module_filesearch_subtitle": "RAG Engine (Token Overlap)",
        "module_filesearch_desc": "Token overlap-based retrieval with native Korean HWP support. RAG engine optimized for Korean academic workflows, with automatic indexing at 03:00 KST daily enabling evidence tracking.",
        "module_filesearch_status": "Beta - Active Development",
        
        "module_youtube_title": "Youtube",
        "module_youtube_subtitle": "YouTube Integration",
        "module_youtube_desc": "Full YouTube integration for research and learning workflows. YouTube Data API v3 supports search, queue management, and embedded player, with Live2D character in Speaking state describing video content.",
        "module_youtube_status": "Production Ready",
        
        "module_fileedit_title": "FileEdit",
        "module_fileedit_subtitle": "Canvas Workspace",
        "module_fileedit_desc": "Collaborative workspace supporting multi-format export. Local draft storage (no server uploads) for document creation and editing, with Live2D character in Thinking state during long drafts.",
        "module_fileedit_status": "Beta - Under Refinement",
        
        "module_users_title": "Users",
        "module_users_subtitle": "Multi-tenant Context",
        "module_users_desc": "Enterprise-grade multi-tenancy for team deployments. Scoped by org-id and project-id, with per-tenant API keys isolating credentials. Cost tagging and audit trails ensure full accountability.",
        "module_users_status": "Production Ready",
        
        "module_monitor_title": "MonitorCheck",
        "module_monitor_subtitle": "Windows Agent",
        "module_monitor_desc": "Windows environment monitoring agent (beta). Tracks system status and integrates with Live2D character to report system events in real-time.",
        "module_monitor_status": "Beta - Windows Agent",
        
        "module_activity_title": "Activity",
        "module_activity_subtitle": "Activity Metrics",
        "module_activity_desc": "Alpha-stage activity metrics tracking system. Logs and analyzes all of Ceria's actions to measure usage patterns and efficiency.",
        "module_activity_status": "Alpha - Metrics Only",
        
        # Pricing Page
        "pricing_free_title": "FREE",
        "pricing_free_price": "$0",
        "pricing_free_period": "Forever free",
        "pricing_free_desc": "Essential features for individual users",
        "pricing_free_feature1": "✅ Live2D Character Assistant (Haru model)",
        "pricing_free_feature2": "✅ Basic conversation (Claude Sonnet 4)",
        "pricing_free_feature3": "✅ Local file processing (up to 100 files)",
        "pricing_free_feature4": "✅ ShieldCheck approval system",
        "pricing_free_feature5": "✅ Korean/English support",
        "pricing_free_feature6": "❌ Advanced modules (Youtube, FileSearch)",
        "pricing_free_feature7": "❌ Team collaboration",
        "pricing_free_feature8": "❌ API access",
        
        "pricing_plus_title": "PLUS",
        "pricing_plus_price": "$29",
        "pricing_plus_period": "/month",
        "pricing_plus_desc": "Advanced features for professionals",
        "pricing_plus_badge": "Popular",
        "pricing_plus_feature1": "✅ All FREE features",
        "pricing_plus_feature2": "✅ Claude Sonnet 4.5 (latest model)",
        "pricing_plus_feature3": "✅ All 8 modules available",
        "pricing_plus_feature4": "✅ FileSearch RAG engine (unlimited)",
        "pricing_plus_feature5": "✅ Youtube integration (1hr caching)",
        "pricing_plus_feature6": "✅ Canvas workspace (unlimited)",
        "pricing_plus_feature7": "✅ Priority support (24hr response)",
        "pricing_plus_feature8": "❌ Team multi-tenancy",
        
        "pricing_pro_title": "PRO",
        "pricing_pro_price": "$99",
        "pricing_pro_period": "/month",
        "pricing_pro_desc": "Enterprise solution for organizations",
        "pricing_pro_badge": "Recommended",
        "pricing_pro_feature1": "✅ All PLUS features",
        "pricing_pro_feature2": "✅ Multi-tenant support (unlimited org/project)",
        "pricing_pro_feature3": "✅ Team collaboration (up to 50 members)",
        "pricing_pro_feature4": "✅ API access (REST + SSE)",
        "pricing_pro_feature5": "✅ Custom Live2D model support",
        "pricing_pro_feature6": "✅ Dedicated server instance",
        "pricing_pro_feature7": "✅ Audit logs & cost tagging",
        "pricing_pro_feature8": "✅ VIP support (1hr response)",
        
        # Dashboard Page
        "dashboard_realtime_title": "실시간 모니터링",
        "dashboard_ceria_status": "세리아 상태",
        "dashboard_current_task": "현재 작업",
        "dashboard_approval_queue": "승인 대기",
        "dashboard_recent_activity": "최근 활동",
        "dashboard_system_health": "시스템 상태",
        "dashboard_task_history": "작업 이력",
        "dashboard_no_tasks": "진행 중인 작업이 없습니다",
        "dashboard_pending_approvals": "개 승인 대기",
        
        # Canvas Page
        "canvas_workspace_title": "작업 공간",
        "canvas_ai_suggestions": "AI 제안",
        "canvas_export": "내보내기",
        "canvas_save_draft": "임시 저장",
        "canvas_format_markdown": "Markdown",
        "canvas_format_pdf": "PDF",
        "canvas_format_docx": "DOCX",
        "canvas_placeholder": "여기에 내용을 작성하세요... (Markdown 지원)",
        "canvas_ai_assist": "AI 어시스턴트",
        "canvas_ask_ceria": "세리아에게 질문하기",
        
        # Developer Profile Section
        "developer_title": "About Developer",
        "developer_name": "Prof. Nam Hyunwoo",
        "developer_affiliation": "Seokyeong University, VD_Visual Design, Contents System",
        "developer_specialty": "AI, Blockchain, IoT, XR",
        "developer_website": "DXPIA.com",
        "developer_research_title": "Research Interests",
        "developer_research_1": "ICT Strategy & Contents System Design",
        "developer_research_2": "AI Agent Systems & Human-in-the-loop Interface",
        "developer_research_3": "Blockchain-based ART NFT Platform",
        "developer_research_4": "IoT-based Beauty AI Service System",
        "developer_research_5": "XR(VR/AR/MR) & Metaverse Contents Strategy",
        "developer_vision_title": "Project Vision",
        "developer_vision_content": "NEXUS-ON presents a new paradigm of human-AI collaboration. With a local-first architecture ensuring data safety, perfect processing of Korean documents including HWP, and transparent operation always under user control, we aim to create a trustworthy AI assistant.",
        "developer_philosophy_title": "Development Philosophy",
        "developer_philosophy_1": "Local-first: Secure data processing without cloud uploads",
        "developer_philosophy_2": "Human oversight: Critical decisions always require user approval",
        "developer_philosophy_3": "Fail-safe: Return to safe default state on errors",
        "developer_philosophy_4": "Open by design: Open-source project for education and research",
        "developer_contact_title": "Contact",
        "developer_contact_dept": "Seokyeong University, VD_Visual Design",
        "developer_contact_lab": "Contents System Lab (AI, Blockchain, IoT, XR)",
        "developer_contact_website": "DXPIA.com",
        "developer_contact_project": "NEXUS-ON Open Source Project",
        
        # Dashboard Page (English)
        "dashboard_realtime_title": "Real-time Monitoring",
        "dashboard_ceria_status": "Ceria Status",
        "dashboard_current_task": "Current Task",
        "dashboard_approval_queue": "Approval Queue",
        "dashboard_recent_activity": "Recent Activity",
        "dashboard_system_health": "System Health",
        "dashboard_task_history": "Task History",
        "dashboard_no_tasks": "No tasks in progress",
        "dashboard_pending_approvals": "pending approvals",
        
        # Canvas Page (English)
        "canvas_workspace_title": "Workspace",
        "canvas_ai_suggestions": "AI Suggestions",
        "canvas_export": "Export",
        "canvas_save_draft": "Save Draft",
        "canvas_format_markdown": "Markdown",
        "canvas_format_pdf": "PDF",
        "canvas_format_docx": "DOCX",
        "canvas_placeholder": "Start writing here... (Markdown supported)",
        "canvas_ai_assist": "AI Assistant",
        "canvas_ask_ceria": "Ask Ceria",
    }
}


def t(key: str, lang: str = "ko") -> str:
    """Translation helper."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["ko"]).get(key, key)


def render_live2d_component(page_state: str = 'idle') -> str:
    """
    Render Live2D character component with real Live2D SDK.
    
    Args:
        page_state: Initial character state (idle/listening/thinking/speaking/busy)
    
    Returns:
        HTML string for Live2D component
    """
    return f'''
    <!-- Live2D Character Container -->
    <div id="live2d-container" class="live2d-container loading" data-status="{page_state}">
        <!-- Live2D canvas will be injected here -->
    </div>

    <!-- Live2D Styles -->
    <link rel="stylesheet" href="/static/css/live2d.css">

    <!-- PIXI.js v7.x (Required for Live2D) -->
    <script src="https://cdn.jsdelivr.net/npm/pixi.js@7.3.2/dist/pixi.min.js"></script>
    
    <!-- Live2D Cubism Core -->
    <script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
    
    <!-- pixi-live2d-display (LOCAL) -->
    <script src="/static/js/pixi-live2d-display.min.js"></script>

    <!-- Live2D Manager -->
    <script src="/static/js/live2d-loader.js"></script>

    <!-- TTS Manager -->
    <script src="/static/js/tts-manager.js"></script>

    <!-- Initialize Live2D -->
    <script>
        let live2dManager = null;
        
        window.addEventListener('DOMContentLoaded', () => {{
            try {{
                const container = document.getElementById('live2d-container');
                if (!container) {{
                    console.error('❌ Live2D container not found');
                    return;
                }}

                // Show loading state
                container.classList.add('loading');

                // Initialize Live2D Manager
                setTimeout(() => {{
                    try {{
                        live2dManager = new Live2DManager(
                            'live2d-container',
                            '/live2d/haru_greeter_t05.model3.json'
                        );
                        
                        // Set initial state
                        setTimeout(() => {{
                            if (live2dManager && live2dManager.model) {{
                                live2dManager.setState('{page_state}');
                                container.classList.remove('loading');
                                console.log('✅ Live2D initialized with state: {page_state}');
                            }}
                        }}, 1000);
                        
                    }} catch (error) {{
                        console.error('❌ Live2D initialization error:', error);
                        container.classList.remove('loading');
                        container.classList.add('error');
                    }}
                }}, 500);
                
            }} catch (error) {{
                console.error('❌ Live2D setup error:', error);
            }}
        }});
        
        // Make globally available for state changes
        window.nexusCharacter = function() {{
            return {{
                setState: (state) => {{
                    if (live2dManager) {{
                        live2dManager.setState(state);
                    }}
                }},
                hide: () => {{
                    const container = document.getElementById('live2d-container');
                    if (container) container.style.display = 'none';
                }},
                show: () => {{
                    const container = document.getElementById('live2d-container');
                    if (container) container.style.display = 'block';
                }}
            }};
        }};
    </script>
    '''



def render_world_class_styles() -> str:
    """NEXUS UI v2.0 - World-Class Design System with i18n support."""
    return """
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
      
      :root {
        /* Dark Navigation Colors */
        --nav-bg: #1A1A1A;
        --nav-text: #FFFFFF;
        --nav-text-dim: #B4B4B4;
        --nav-border: rgba(255, 255, 255, 0.1);
        
        /* Colors */
        --bg-primary: #FFFFFF;
        --bg-secondary: #F7F7F8;
        --bg-dark: #0A0A0A;
        --text-primary: #111111;
        --text-secondary: #3C3C43;
        --text-tertiary: #6B6B73;
        --accent-primary: #3B82F6;
        --accent-hover: #2563EB;
        --accent-soft: #EFF6FF;
        --accent-gold: #F59E0B;
        --border-default: #E6E6EA;
        --border-strong: #D1D1D6;
        
        /* Gradients */
        --gradient-hero: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 30%, #DBEAFE 100%);
        --gradient-accent: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        --gradient-gold: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        --gradient-card: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 250, 251, 0.95) 100%);
        --gradient-card-hover: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(37, 99, 235, 0.12) 100%);
        --gradient-dark: linear-gradient(135deg, #1A1A1A 0%, #0A0A0A 100%);
        
        /* Status Colors */
        --status-green: #10B981;
        --status-yellow: #F59E0B;
        --status-red: #EF4444;
        --status-blue: #3B82F6;
        
        /* Typography */
        --font-sans: -apple-system, BlinkMacSystemFont, "Pretendard Variable", Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
        --font-mono: "SF Mono", "Consolas", "Monaco", monospace;
        --text-4xl: 56px;
        --text-3xl: 48px;
        --text-2xl: 36px;
        --text-xl: 24px;
        --text-lg: 18px;
        --text-base: 16px;
        --text-sm: 14px;
        --text-xs: 12px;
        
        /* Spacing */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 20px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;
        --space-16: 64px;
        --space-20: 80px;
        --space-24: 96px;
        
        /* Radius */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-card: 24px;
        --radius-pill: 999px;
        
        /* Shadow */
        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
        --shadow-2xl: 0 24px 64px rgba(0, 0, 0, 0.20);
        
        /* Motion */
        --duration-fast: 120ms;
        --duration-ui: 180ms;
        --duration-slow: 280ms;
        --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
        --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
      }
      
      * { box-sizing: border-box; margin: 0; padding: 0; }
      
      body {
        font-family: var(--font-sans);
        font-size: var(--text-base);
        color: var(--text-primary);
        background: var(--bg-primary);
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
      }
      
      /* Animations */
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
      }
      
      @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
        50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.6); }
      }
      
      @keyframes slide-in-up {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      @keyframes slide-in-left {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
      }
      
      @keyframes slide-in-right {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
      }
      
      @keyframes fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      
      @keyframes scale-in {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
      }
      
      @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
      }
      
      /* Navigation - Dark Premium Theme */
      nav {
        background: var(--nav-bg);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--nav-border);
        padding: var(--space-4) var(--space-8);
        display: flex;
        align-items: center;
        gap: var(--space-6);
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5);
      }
      
      .nav-brand {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        font-size: var(--text-xl);
        font-weight: 700;
        color: var(--nav-text);
        text-decoration: none;
        margin-right: auto;
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .nav-brand:hover {
        transform: translateY(-2px);
        filter: brightness(1.2);
      }
      
      .nav-logo {
        width: 40px;
        height: 40px;
        border-radius: var(--radius-md);
        background: var(--gradient-accent);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .nav-brand:hover .nav-logo {
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.6);
        transform: rotate(5deg) scale(1.05);
      }
      
      .nav-logo img {
        width: 28px;
        height: 28px;
        object-fit: contain;
      }
      
      .nav-links {
        display: flex;
        align-items: center;
        gap: var(--space-2);
      }
      
      .nav-link {
        color: var(--nav-text-dim);
        text-decoration: none;
        font-size: var(--text-sm);
        font-weight: 500;
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-md);
        transition: all var(--duration-ui) var(--ease-out);
        position: relative;
      }
      
      .nav-link:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--nav-text);
        transform: translateY(-2px);
      }
      
      .nav-link.active {
        background: var(--gradient-accent);
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
      }
      
      .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: -16px;
        left: 50%;
        transform: translateX(-50%);
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: var(--accent-primary);
        box-shadow: 0 0 8px var(--accent-primary);
      }
      
      /* Language Toggle Button */
      .lang-toggle {
        padding: var(--space-2) var(--space-4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.05);
        color: var(--nav-text);
        border-radius: var(--radius-pill);
        font-size: var(--text-xs);
        font-weight: 600;
        cursor: pointer;
        transition: all var(--duration-ui) var(--ease-out);
        backdrop-filter: blur(10px);
      }
      
      .lang-toggle:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        transform: scale(1.05);
      }
      
      @media (max-width: 768px) {
        nav {
          padding: var(--space-3) var(--space-4);
          gap: var(--space-3);
        }
        
        .nav-links {
          display: none; /* Hide on mobile - implement hamburger menu later */
        }
        
        .nav-logo {
          width: 32px;
          height: 32px;
        }
        
        .nav-logo img {
          width: 20px;
          height: 20px;
        }
      }
      
      /* Hero Section */
      .hero-world-class {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--gradient-hero);
        position: relative;
        overflow: hidden;
        padding: var(--space-12) var(--space-6);
      }
      
      .hero-content {
        max-width: 1200px;
        margin: 0 auto;
        text-align: center;
        position: relative;
        z-index: 2;
        animation: slide-in-up 0.8s var(--ease-out);
      }
      
      .hero-character {
        width: 400px;
        height: 480px;
        margin: 0 auto var(--space-8);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(239, 246, 255, 0.8) 100%);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(255, 255, 255, 0.5);
        border-radius: var(--radius-card);
        box-shadow: var(--shadow-xl);
        display: flex;
        align-items: center;
        justify-content: center;
        animation: float 4s ease-in-out infinite;
        position: relative;
      }
      
      .hero-character::before {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: var(--radius-card);
        padding: 2px;
        background: var(--gradient-accent);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        animation: pulse-glow 2s ease-in-out infinite;
      }
      
      .character-placeholder {
        font-size: 120px;
        opacity: 0.6;
      }
      
      .character-state {
        position: absolute;
        bottom: var(--space-4);
        left: 50%;
        transform: translateX(-50%);
        background: rgba(37, 99, 235, 0.9);
        color: white;
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-pill);
        font-size: var(--text-sm);
        font-weight: 600;
      }
      
      .hero-title {
        font-size: var(--text-3xl);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-4);
        line-height: 1.2;
      }
      
      .hero-subtitle {
        font-size: var(--text-xl);
        color: var(--text-secondary);
        margin-bottom: var(--space-8);
        font-weight: 500;
      }
      
      .hero-tagline {
        font-size: var(--text-lg);
        color: var(--text-tertiary);
        max-width: 700px;
        margin: 0 auto var(--space-8);
        line-height: 1.75;
      }
      
      /* Hero Input Container (AI Chat) */
      .hero-input-container {
        max-width: 700px;
        margin: 0 auto var(--space-8);
        padding: 0 var(--space-4);
      }
      
      .hero-input-wrapper {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(37, 99, 235, 0.15);
        border-radius: var(--radius-control);
        padding: var(--space-2);
        box-shadow: var(--shadow-lg);
        transition: all var(--duration-ui) var(--ease-out);
      }
      
      .hero-input-wrapper:focus-within {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1), var(--shadow-lg);
      }
      
      .hero-input {
        flex: 1;
        border: none;
        background: transparent;
        font-size: var(--text-base);
        color: var(--text-primary);
        padding: var(--space-3) var(--space-4);
        outline: none;
        font-family: var(--font-sans);
      }
      
      .hero-input::placeholder {
        color: var(--text-tertiary);
      }
      
      .hero-voice-btn,
      .hero-send-btn {
        width: 44px;
        height: 44px;
        border: none;
        border-radius: var(--radius-control);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all var(--duration-ui) var(--ease-out);
        font-size: 20px;
      }
      
      .hero-voice-btn {
        background: var(--bg-secondary);
        color: var(--text-primary);
      }
      
      .hero-voice-btn:hover {
        background: var(--accent-soft);
        transform: scale(1.05);
      }
      
      .hero-voice-btn:active {
        transform: scale(0.95);
      }
      
      .hero-send-btn {
        background: var(--gradient-accent);
        color: white;
        font-weight: 600;
      }
      
      .hero-send-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
      }
      
      .hero-send-btn:active {
        transform: scale(0.95);
      }
      
      .hero-cta-group {
        display: flex;
        gap: var(--space-4);
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
      }
      
      /* Glassmorphism Buttons */
      .btn-glass-primary {
        display: inline-block;
        padding: var(--space-4) var(--space-8);
        background: var(--gradient-accent);
        color: white;
        border-radius: var(--radius-pill);
        font-size: var(--text-lg);
        font-weight: 600;
        text-decoration: none;
        box-shadow: var(--shadow-lg);
        transition: all var(--duration-ui) var(--ease-out);
        border: none;
        cursor: pointer;
      }
      
      .btn-glass-primary:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
      }
      
      .btn-glass-secondary {
        display: inline-block;
        padding: var(--space-4) var(--space-8);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        color: var(--accent-primary);
        border: 2px solid var(--accent-primary);
        border-radius: var(--radius-pill);
        font-size: var(--text-lg);
        font-weight: 600;
        text-decoration: none;
        box-shadow: var(--shadow-md);
        transition: all var(--duration-ui) var(--ease-out);
        cursor: pointer;
      }
      
      .btn-glass-secondary:hover {
        background: var(--accent-soft);
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
      }
      
      /* Core Values */
      .core-values {
        padding: var(--space-20) var(--space-6);
        background: var(--bg-primary);
      }
      
      .core-values-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: var(--space-8);
        max-width: 1200px;
        margin: 0 auto;
      }
      
      .value-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: var(--radius-card);
        padding: var(--space-8);
        box-shadow: var(--shadow-md);
        transition: all var(--duration-ui) var(--ease-out);
        text-align: center;
      }
      
      .value-card:hover {
        transform: translateY(-8px);
        box-shadow: var(--shadow-xl);
        background: var(--gradient-card-hover);
      }
      
      .value-icon {
        font-size: 64px;
        margin-bottom: var(--space-4);
      }
      
      .value-title {
        font-size: var(--text-xl);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-3);
      }
      
      .value-desc {
        font-size: var(--text-base);
        color: var(--text-secondary);
        line-height: 1.75;
      }
      
      /* Container */
      .container {
        max-width: 1240px;
        margin: 0 auto;
        padding: var(--space-12) var(--space-6);
      }
      
      .section-title {
        font-size: var(--text-2xl);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-8);
        text-align: center;
      }
      
      .section-subtitle {
        font-size: var(--text-lg);
        color: var(--text-secondary);
        max-width: 700px;
        margin: 0 auto var(--space-12);
        text-align: center;
        line-height: 1.75;
      }
      
      /* Footer */
      footer {
        background: var(--bg-secondary);
        padding: var(--space-12) var(--space-6);
        text-align: center;
        border-top: 1px solid var(--border-default);
      }
      
      footer p {
        color: var(--text-tertiary);
        font-size: var(--text-sm);
      }
      
      /* Responsive */
      @media (max-width: 768px) {
        .hero-character {
          width: 280px;
          height: 320px;
        }
        
        .character-placeholder {
          font-size: 80px;
        }
        
        .hero-title {
          font-size: var(--text-2xl);
        }
        
        .hero-subtitle {
          font-size: var(--text-lg);
        }
        
        .hero-input-container {
          padding: 0 var(--space-2);
        }
        
        .hero-input-wrapper {
          flex-wrap: nowrap;
        }
        
        .hero-voice-btn,
        .hero-send-btn {
          width: 40px;
          height: 40px;
          font-size: 18px;
        }
        
        .hero-cta-group {
          flex-direction: column;
          gap: var(--space-3);
        }
        
        .btn-glass-primary,
        .btn-glass-secondary {
          font-size: var(--text-base);
          padding: var(--space-3) var(--space-6);
          width: 100%;
          max-width: 300px;
        }
      }
    </style>
    """


def render_navigation(current_page: str = "", lang: str = "ko") -> str:
    """Render premium dark navigation with logo."""
    nav_items = [
        (t("nav_home", lang), "/"),
        (t("nav_intro", lang), "/intro"),
        (t("nav_modules", lang), "/modules"),
        (t("nav_pricing", lang), "/pricing"),
        (t("nav_dashboard", lang), "/dashboard-preview"),
        (t("nav_canvas", lang), "/canvas-preview"),
        (t("nav_login", lang), "/login"),
    ]
    
    other_lang = "en" if lang == "ko" else "ko"
    lang_label = "EN" if lang == "ko" else "한국어"
    
    nav_html = "<nav>"
    # Brand with logo
    nav_html += '''
    <a href="/" class="nav-brand">
        <div class="nav-logo">
            <img src="/static/images/nexus-on-logo.png" alt="NEXUS-ON" />
        </div>
        <span>NEXUS-ON</span>
    </a>
    '''
    
    # Navigation links
    nav_html += '<div class="nav-links">'
    for label, path in nav_items:
        active_class = "active" if path == current_page else ""
        nav_html += f'<a href="{path}?lang={lang}" class="nav-link {active_class}">{label}</a>'
    nav_html += '</div>'
    
    # Language toggle
    nav_html += f'<button class="lang-toggle" onclick="toggleLanguage()">{lang_label}</button>'
    
    # Language toggle script
    nav_html += """
    <script>
    function toggleLanguage() {
        const url = new URL(window.location.href);
        const currentLang = url.searchParams.get('lang') || 'ko';
        const newLang = currentLang === 'ko' ? 'en' : 'ko';
        url.searchParams.set('lang', newLang);
        window.location.href = url.toString();
    }
    </script>
    """
    nav_html += "</nav>"
    return nav_html


def render_footer(lang: str = "ko") -> str:
    """Render footer."""
    return f"""
    <footer>
        <p>&copy; 2026 NEXUS-ON. {t("footer_text", lang)}</p>
        <p>{t("footer_dev", lang)}</p>
    </footer>
    """


def landing_page(lang: str = "ko") -> str:
    """Render world-class landing page with i18n support and Live2D character."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS-ON | {t("hero_subtitle", lang)}</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="idle">
        {render_navigation("/", lang)}
        
        <!-- Live2D Character (Idle state for landing) -->
        {render_live2d_component("idle")}
        
        <!-- HERO SECTION -->
        <section class="hero-world-class">
            <div class="hero-content">
                <h1 class="hero-title">{t("hero_title", lang)}</h1>
                <p class="hero-subtitle">{t("hero_subtitle", lang)}</p>
                <p class="hero-tagline">{t("hero_tagline", lang)}</p>
                
                <!-- AI Chat Input UI (Below Live2D Character) -->
                <div class="hero-input-container">
                    <div class="hero-input-wrapper">
                        <input 
                            type="text" 
                            class="hero-input" 
                            placeholder="{t('hero_input_placeholder', lang)}"
                            id="hero-chat-input"
                        />
                        <button class="hero-voice-btn" id="voice-input-btn" title="{t('hero_voice_button', lang)}">
                            🎤
                        </button>
                        <button class="hero-send-btn" id="send-btn" title="{t('hero_text_button', lang)}">
                            →
                        </button>
                    </div>
                </div>
                
                <div class="hero-cta-group">
                    <a href="/signup?lang={lang}" class="btn-glass-primary">{t("hero_cta_primary", lang)}</a>
                    <a href="#demo" class="btn-glass-secondary">{t("hero_cta_secondary", lang)}</a>
                </div>
            </div>
        </section>
        
        <!-- 3 CORE VALUES -->
        <section class="core-values">
            <div class="core-values-grid">
                <div class="value-card">
                    <div class="value-icon">🎭</div>
                    <h3 class="value-title">{t("value1_title", lang)}</h3>
                    <p class="value-desc">{t("value1_desc", lang)}</p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🤖</div>
                    <h3 class="value-title">{t("value2_title", lang)}</h3>
                    <p class="value-desc">{t("value2_desc", lang)}</p>
                </div>
                
                <div class="value-card">
                    <div class="value-icon">🇰🇷</div>
                    <h3 class="value-title">{t("value3_title", lang)}</h3>
                    <p class="value-desc">{t("value3_desc", lang)}</p>
                </div>
            </div>
        </section>
        
        {render_footer(lang)}
        
        <!-- Chat Input & Voice Interaction -->
        <script>
            // Chat input handler
            const chatInput = document.getElementById('hero-chat-input');
            const sendBtn = document.getElementById('send-btn');
            const voiceBtn = document.getElementById('voice-input-btn');
            const character = window.nexusCharacter();
            
            // Send message
            function sendMessage() {{
                const message = chatInput.value.trim();
                if (!message) return;
                
                console.log('Sending message:', message);
                if (character) character.setState('thinking');
                
                // Simulate response
                setTimeout(() => {{
                    if (character) character.setState('speaking');
                    setTimeout(() => {{
                        if (character) character.setState('idle');
                    }}, 2000);
                }}, 1000);
                
                chatInput.value = '';
            }}
            
            sendBtn.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') sendMessage();
            }});
            
            // Voice input
            voiceBtn.addEventListener('click', () => {{
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    const recognition = new SpeechRecognition();
                    recognition.lang = '{lang}';
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    
                    recognition.onstart = () => {{
                        if (character) character.setState('listening');
                        voiceBtn.style.background = 'var(--accent-primary)';
                        voiceBtn.style.color = 'white';
                    }};
                    
                    recognition.onresult = (event) => {{
                        const transcript = event.results[0][0].transcript;
                        chatInput.value = transcript;
                        if (character) character.setState('thinking');
                    }};
                    
                    recognition.onend = () => {{
                        voiceBtn.style.background = '';
                        voiceBtn.style.color = '';
                        if (character) character.setState('idle');
                    }};
                    
                    recognition.onerror = (event) => {{
                        console.error('Speech recognition error:', event.error);
                        voiceBtn.style.background = '';
                        voiceBtn.style.color = '';
                        if (character) character.setState('idle');
                    }};
                    
                    recognition.start();
                }} else {{
                    alert('{t("voice_not_supported", lang)}');
                }}
            }});
        </script>
        
        <!-- Scroll-based state changes -->
        <script>
            window.addEventListener('scroll', function() {{
                const scrollY = window.scrollY;
                const character = window.nexusCharacter();
                if (!character) return;
                
                if (scrollY < 300) {{
                    character.setState('idle');
                }} else if (scrollY < 600) {{
                    character.setState('listening');
                }} else {{
                    character.setState('thinking');
                }}
            }});
        </script>
    </body>
    </html>
    """


def pricing_page(lang: str = "ko") -> str:
    """Render pricing page with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_pricing", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="thinking">
        {render_navigation("/pricing", lang)}
        
        <!-- Live2D Character (Thinking state for pricing) -->
        {render_live2d_component("thinking")}
        
        <div class="container">
            <h1 class="section-title">{t("pricing_title", lang)}</h1>
            <p class="section-subtitle">{t("pricing_subtitle", lang)}</p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">💳</div>
                <p style="font-size: 18px;">{t("pricing_coming", lang)}</p>
                <p>{t("pricing_plans", lang)}</p>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def dashboard_preview_page(lang: str = "ko") -> str:
    """Render dashboard preview with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_dashboard", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="busy">
        {render_navigation("/dashboard-preview", lang)}
        
        <!-- Live2D Character (Busy state for dashboard) -->
        {render_live2d_component("busy")}
        
        <div class="container">
            <h1 class="section-title">{t("dashboard_title", lang)}</h1>
            <p class="section-subtitle">{t("dashboard_subtitle", lang)}</p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">📊</div>
                <p style="font-size: 18px;">{t("dashboard_coming", lang)}</p>
                <p>{t("dashboard_features", lang)}</p>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def canvas_preview_page(lang: str = "ko") -> str:
    """Render canvas workspace with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_canvas", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="thinking">
        {render_navigation("/canvas-preview", lang)}
        
        <!-- Live2D Character (Thinking state for canvas) -->
        {render_live2d_component("thinking")}
        
        <div class="container">
            <h1 class="section-title">{t("canvas_title", lang)}</h1>
            <p class="section-subtitle">{t("canvas_subtitle", lang)}</p>
            
            <div style="text-align: center; padding: 100px 0; color: var(--text-tertiary);">
                <div style="font-size: 64px; margin-bottom: 24px;">📝</div>
                <p style="font-size: 18px;">{t("canvas_coming", lang)}</p>
                <p>{t("canvas_features", lang)}</p>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def login_page(lang: str = "ko") -> str:
    """Render login page with i18n."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_login", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="idle">
        {render_navigation("/login", lang)}
        
        <!-- Live2D Character (Idle state for login) -->
        {render_live2d_component("idle")}
        
        <div class="container">
            <div style="text-align: center; padding: 100px 0;">
                <div style="font-size: 64px; margin-bottom: 24px;">🔐</div>
                <h1 class="section-title">{t("login_title", lang)}</h1>
                <p class="section-subtitle">{t("login_subtitle", lang)}</p>
                
                <div style="max-width: 400px; margin: 48px auto; text-align: left;">
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">{t("login_email", lang)}</label>
                        <input type="email" placeholder="your@email.com" 
                               style="width: 100%; padding: 12px 16px; border: 1px solid var(--border-default); 
                                      border-radius: var(--radius-control); font-size: var(--text-base);">
                    </div>
                    
                    <div style="margin-bottom: 24px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">{t("login_password", lang)}</label>
                        <input type="password" placeholder="••••••••" 
                               style="width: 100%; padding: 12px 16px; border: 1px solid var(--border-default); 
                                      border-radius: var(--radius-control); font-size: var(--text-base);">
                    </div>
                    
                    <button class="btn-glass-primary" style="width: 100%; margin-bottom: 16px;">{t("login_button", lang)}</button>
                    
                    <div style="text-align: center; color: var(--text-tertiary); font-size: var(--text-sm);">
                        {t("login_no_account", lang)} <a href="/signup?lang={lang}" style="color: var(--accent-primary);">{t("login_signup", lang)}</a>
                    </div>
                </div>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def intro_page(lang: str = "ko") -> str:
    """Render world-class introduction page with 6 differentiators."""
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_intro", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
        <style>
            .intro-hero {{
                background: var(--gradient-hero);
                padding: var(--space-20) var(--space-6);
                text-align: center;
            }}
            
            .intro-hero h1 {{
                font-size: var(--text-4xl);
                font-weight: 800;
                color: var(--text-primary);
                margin-bottom: var(--space-6);
                background: var(--gradient-accent);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .intro-hero p {{
                font-size: var(--text-xl);
                color: var(--text-secondary);
                max-width: 800px;
                margin: 0 auto var(--space-12);
                line-height: 1.8;
            }}
            
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
                gap: var(--space-8);
                max-width: 1400px;
                margin: 0 auto;
                padding: var(--space-12) var(--space-6);
            }}
            
            .feature-card {{
                background: var(--gradient-card);
                border-radius: var(--radius-xl);
                padding: var(--space-10);
                box-shadow: var(--shadow-lg);
                border: 1px solid var(--border-default);
                transition: all var(--duration-slow) var(--ease-out);
                position: relative;
                overflow: hidden;
            }}
            
            .feature-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--gradient-accent);
                transform: scaleX(0);
                transform-origin: left;
                transition: transform var(--duration-slow) var(--ease-out);
            }}
            
            .feature-card:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: var(--shadow-2xl);
                border-color: var(--accent-primary);
            }}
            
            .feature-card:hover::before {{
                transform: scaleX(1);
            }}
            
            .feature-icon {{
                font-size: 48px;
                margin-bottom: var(--space-4);
                display: block;
            }}
            
            .feature-title {{
                font-size: var(--text-2xl);
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: var(--space-4);
            }}
            
            .feature-content {{
                font-size: var(--text-base);
                color: var(--text-secondary);
                line-height: 1.8;
            }}
            
            @media (max-width: 768px) {{
                .features-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .intro-hero h1 {{
                    font-size: var(--text-3xl);
                }}
            }}
        </style>
    </head>
    <body data-page-state="listening">
        {render_navigation("/intro", lang)}
        
        <!-- Live2D Character (Listening state for intro) -->
        {render_live2d_component("listening")}
        
        <!-- Hero Section -->
        <section class="intro-hero">
            <h1>{t("intro_worldclass_title", lang)}</h1>
            <p>{t("intro_worldclass_subtitle", lang)}</p>
        </section>
        
        <!-- Features Grid -->
        <section class="features-grid">
            <!-- Feature 1: Live2D Character -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.1s both;">
                <span class="feature-icon">{t("intro_feature1_title", lang).split()[0]}</span>
                <h2 class="feature-title">{' '.join(t("intro_feature1_title", lang).split()[1:])}</h2>
                <p class="feature-content">{t("intro_feature1_content", lang)}</p>
            </article>
            
            <!-- Feature 2: ShieldCheck -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.2s both;">
                <span class="feature-icon">{t("intro_feature2_title", lang).split()[0]}</span>
                <h2 class="feature-title">{' '.join(t("intro_feature2_title", lang).split()[1:])}</h2>
                <p class="feature-content">{t("intro_feature2_content", lang)}</p>
            </article>
            
            <!-- Feature 3: Korean Native -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.3s both;">
                <span class="feature-icon">{t("intro_feature3_title", lang).split()[0]}</span>
                <h2 class="feature-title">{' '.join(t("intro_feature3_title", lang).split()[1:])}</h2>
                <p class="feature-content">{t("intro_feature3_content", lang)}</p>
            </article>
            
            <!-- Feature 4: Multi-Agent -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.4s both;">
                <span class="feature-icon">{t("intro_feature4_title", lang).split()[0]}</span>
                <h2 class="feature-title">{' '.join(t("intro_feature4_title", lang).split()[1:])}</h2>
                <p class="feature-content">{t("intro_feature4_content", lang)}</p>
            </article>
            
            <!-- Feature 5: Local-first -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.5s both;">
                <span class="feature-icon">{t("intro_feature5_title", lang).split()[0]}</span>
                <h2 class="feature-title">{' '.join(t("intro_feature5_title", lang).split()[1:])}</h2>
                <p class="feature-content">{t("intro_feature5_content", lang)}</p>
            </article>
            
            <!-- Feature 6: Real-time Monitoring -->
            <article class="feature-card" style="animation: slide-in-up 0.6s var(--ease-out) 0.6s both;">
                <span class="feature-icon">{t("intro_feature6_title", lang).split()[0]}</span>
                <h2 class="feature-title">{' '.join(t("intro_feature6_title", lang).split()[1:])}</h2>
                <p class="feature-content">{t("intro_feature6_content", lang)}</p>
            </article>
        </section>
        
        <div class="container">
                
                <!-- Developer Profile Section -->
                <div style="background: var(--gradient-card); padding: var(--space-10); border-radius: var(--radius-card); margin-top: var(--space-8); border: 2px solid var(--accent-soft);">
                    <h2 style="font-size: var(--text-2xl); font-weight: 700; margin-bottom: var(--space-6); color: var(--text-primary); text-align: center;">
                        👨‍💻 {t("developer_title", lang)}
                    </h2>
                    
                    <div style="text-align: center; margin-bottom: var(--space-8);">
                        <h3 style="font-size: var(--text-xl); font-weight: 600; color: var(--accent-primary); margin-bottom: var(--space-2);">
                            {t("developer_name", lang)}
                        </h3>
                        <p style="font-size: var(--text-base); color: var(--text-tertiary);">
                            {t("developer_affiliation", lang)}
                        </p>
                    </div>
                    
                    <div style="margin-bottom: var(--space-8);">
                        <h4 style="font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-3); color: var(--text-primary);">
                            🔬 {t("developer_research_title", lang)}
                        </h4>
                        <ul style="color: var(--text-secondary); line-height: 2; font-size: var(--text-sm); list-style: none; padding: 0;">
                            <li>• {t("developer_research_1", lang)}</li>
                            <li>• {t("developer_research_2", lang)}</li>
                            <li>• {t("developer_research_3", lang)}</li>
                            <li>• {t("developer_research_4", lang)}</li>
                            <li>• {t("developer_research_5", lang)}</li>
                        </ul>
                    </div>
                    
                    <div style="margin-bottom: var(--space-8);">
                        <h4 style="font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-3); color: var(--text-primary);">
                            🎯 {t("developer_vision_title", lang)}
                        </h4>
                        <p style="color: var(--text-secondary); line-height: 1.75; font-size: var(--text-sm);">
                            {t("developer_vision_content", lang)}
                        </p>
                    </div>
                    
                    <div style="margin-bottom: var(--space-6);">
                        <h4 style="font-size: var(--text-lg); font-weight: 600; margin-bottom: var(--space-3); color: var(--text-primary);">
                            💡 {t("developer_philosophy_title", lang)}
                        </h4>
                        <ul style="color: var(--text-secondary); line-height: 2; font-size: var(--text-sm); list-style: none; padding: 0;">
                            <li>✅ {t("developer_philosophy_1", lang)}</li>
                            <li>✅ {t("developer_philosophy_2", lang)}</li>
                            <li>✅ {t("developer_philosophy_3", lang)}</li>
                            <li>✅ {t("developer_philosophy_4", lang)}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; padding-top: var(--space-6); border-top: 1px solid rgba(0,0,0,0.1);">
                        <h4 style="font-size: var(--text-base); font-weight: 600; margin-bottom: var(--space-2); color: var(--text-primary);">
                            📧 {t("developer_contact_title", lang)}
                        </h4>
                        <p style="font-size: var(--text-sm); color: var(--text-tertiary); margin-bottom: var(--space-2);">
                            {t("developer_contact_dept", lang)}
                        </p>
                        <p style="font-size: var(--text-sm); color: var(--accent-primary);">
                            <a href="https://github.com/multipia-creator/nexus-on" target="_blank" style="color: var(--accent-primary); text-decoration: none;">
                                🔗 {t("developer_contact_project", lang)}
                            </a>
                        </p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: var(--space-12);">
                    <a href="/modules?lang={lang}" class="btn-glass-primary">{t("nav_modules", lang)}</a>
                </div>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def developer_page(lang: str = "ko") -> str:
    """
    Render dedicated developer profile page with 2-column layout.
    
    Layout:
    - Left: Profile image placeholder
    - Right: Detailed profile information
    """
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("developer_title", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
        <style>
            .developer-profile {{
                max-width: 1200px;
                margin: var(--space-20) auto;
                padding: var(--space-6);
            }}
            
            .profile-container {{
                display: grid;
                grid-template-columns: 320px 1fr;
                gap: var(--space-10);
                background: var(--gradient-card);
                border-radius: var(--radius-card);
                padding: var(--space-10);
                box-shadow: var(--shadow-xl);
                border: 2px solid var(--accent-soft);
            }}
            
            @media (max-width: 768px) {{
                .profile-container {{
                    grid-template-columns: 1fr;
                    gap: var(--space-6);
                }}
            }}
            
            .profile-image-section {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: var(--space-4);
            }}
            
            .profile-image-placeholder {{
                width: 280px;
                height: 280px;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                border-radius: var(--radius-card);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 120px;
                box-shadow: var(--shadow-lg);
            }}
            
            .profile-name {{
                font-size: var(--text-2xl);
                font-weight: 700;
                color: var(--accent-primary);
                text-align: center;
                margin-top: var(--space-2);
            }}
            
            .profile-affiliation {{
                font-size: var(--text-base);
                color: var(--text-tertiary);
                text-align: center;
                line-height: 1.6;
            }}
            
            .profile-specialty {{
                font-size: var(--text-sm);
                color: var(--accent-primary);
                font-weight: 600;
                text-align: center;
                margin-top: var(--space-2);
                padding: var(--space-1) var(--space-3);
                background: var(--accent-soft);
                border-radius: var(--radius-pill);
                display: inline-block;
            }}
            
            .profile-website {{
                font-size: var(--text-sm);
                color: var(--accent-primary);
                text-align: center;
                margin-top: var(--space-2);
            }}
            
            .profile-website a {{
                color: var(--accent-primary);
                text-decoration: none;
                font-weight: 600;
                transition: all var(--duration-ui) var(--ease-out);
            }}
            
            .profile-website a:hover {{
                color: var(--accent-secondary);
                text-decoration: underline;
            }}
            
            .profile-info-section {{
                display: flex;
                flex-direction: column;
                gap: var(--space-8);
            }}
            
            .info-block {{
                background: rgba(255, 255, 255, 0.5);
                padding: var(--space-6);
                border-radius: var(--radius-md);
                border-left: 4px solid var(--accent-primary);
            }}
            
            .info-block h3 {{
                font-size: var(--text-xl);
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: var(--space-4);
                display: flex;
                align-items: center;
                gap: var(--space-2);
            }}
            
            .info-block ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .info-block li {{
                color: var(--text-secondary);
                line-height: 1.8;
                font-size: var(--text-sm);
                padding: var(--space-1) 0;
            }}
            
            .info-block li::before {{
                content: "▸";
                color: var(--accent-primary);
                font-weight: bold;
                display: inline-block;
                width: 1em;
                margin-right: var(--space-2);
            }}
            
            .info-block p {{
                color: var(--text-secondary);
                line-height: 1.75;
                font-size: var(--text-sm);
                margin: 0;
            }}
            
            .contact-links {{
                display: flex;
                flex-direction: column;
                gap: var(--space-2);
            }}
            
            .contact-link {{
                display: flex;
                align-items: center;
                gap: var(--space-2);
                color: var(--accent-primary);
                text-decoration: none;
                font-size: var(--text-sm);
                transition: all var(--duration-ui) var(--ease-out);
            }}
            
            .contact-link:hover {{
                transform: translateX(4px);
                color: var(--accent-secondary);
            }}
            
            .back-button {{
                text-align: center;
                margin-top: var(--space-10);
            }}
        </style>
    </head>
    <body data-page-state="friendly">
        {render_navigation("/developer", lang)}
        
        <!-- Live2D Character (Friendly state) -->
        {render_live2d_component("friendly")}
        
        <div class="developer-profile">
            <div class="profile-container">
                <!-- Left Column: Profile Image -->
                <div class="profile-image-section">
                    <div class="profile-image-placeholder">
                        👨‍💻
                    </div>
                    <h2 class="profile-name">{t("developer_name", lang)}</h2>
                    <p class="profile-affiliation">{t("developer_affiliation", lang)}</p>
                    <div class="profile-specialty">
                        {t("developer_specialty", lang)}
                    </div>
                    <div class="profile-website">
                        🌐 <a href="https://dxpia.com" target="_blank">{t("developer_website", lang)}</a>
                    </div>
                </div>
                
                <!-- Right Column: Profile Information -->
                <div class="profile-info-section">
                    <!-- Research Interests -->
                    <div class="info-block">
                        <h3>🔬 {t("developer_research_title", lang)}</h3>
                        <ul>
                            <li>{t("developer_research_1", lang)}</li>
                            <li>{t("developer_research_2", lang)}</li>
                            <li>{t("developer_research_3", lang)}</li>
                            <li>{t("developer_research_4", lang)}</li>
                            <li>{t("developer_research_5", lang)}</li>
                        </ul>
                    </div>
                    
                    <!-- Project Vision -->
                    <div class="info-block">
                        <h3>🎯 {t("developer_vision_title", lang)}</h3>
                        <p>{t("developer_vision_content", lang)}</p>
                    </div>
                    
                    <!-- Development Philosophy -->
                    <div class="info-block">
                        <h3>💡 {t("developer_philosophy_title", lang)}</h3>
                        <ul>
                            <li>{t("developer_philosophy_1", lang)}</li>
                            <li>{t("developer_philosophy_2", lang)}</li>
                            <li>{t("developer_philosophy_3", lang)}</li>
                            <li>{t("developer_philosophy_4", lang)}</li>
                        </ul>
                    </div>
                    
                    <!-- Contact Information -->
                    <div class="info-block">
                        <h3>📧 {t("developer_contact_title", lang)}</h3>
                        <div class="contact-links">
                            <div class="contact-link">
                                🏫 {t("developer_contact_dept", lang)}
                            </div>
                            <div class="contact-link">
                                🔬 {t("developer_contact_lab", lang)}
                            </div>
                            <a href="https://dxpia.com" target="_blank" class="contact-link">
                                🌐 {t("developer_contact_website", lang)}
                            </a>
                            <a href="https://github.com/multipia-creator/nexus-on" target="_blank" class="contact-link">
                                🔗 {t("developer_contact_project", lang)}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="back-button">
                <a href="/?lang={lang}" class="btn-glass-primary">← {t("nav_home", lang)}</a>
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """


def modules_page(lang: str = "ko") -> str:
    """Render modules page with module cards."""
    modules = load_modules_data()
    
    modules_html = ""
    for module in modules:
        status_color = {
            "stable": "var(--status-green)",
            "beta": "var(--status-yellow)",
            "alpha": "var(--status-red)"
        }.get(module.get("status", "alpha"), "var(--status-red)")
        
        modules_html += f"""
        <div class="value-card" style="text-align: left;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4);">
                <div style="font-size: 48px;">{module.get('icon', '📦')}</div>
                <div style="background: {status_color}; color: white; padding: 4px 12px; border-radius: var(--radius-pill); font-size: 12px; font-weight: 600;">
                    {module.get('status_label', module.get('status', 'Unknown'))}
                </div>
            </div>
            <h3 style="font-size: var(--text-xl); font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2);">
                {module.get('name', 'Unknown Module')}
            </h3>
            <p style="font-size: var(--text-sm); color: var(--text-tertiary); margin-bottom: var(--space-4);">
                {module.get('tagline', '')}
            </p>
            <p style="font-size: var(--text-base); color: var(--text-secondary); line-height: 1.6;">
                {module.get('description', '')}
            </p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t("nav_modules", lang)} - NEXUS-ON</title>
        {render_world_class_styles()}
    </head>
    <body data-page-state="speaking">
        {render_navigation("/modules", lang)}
        
        <!-- Live2D Character (Speaking state for modules) -->
        {render_live2d_component("speaking")}
        
        <div class="container">
            <h1 class="section-title">{t("modules_title", lang)}</h1>
            <p class="section-subtitle">{t("modules_subtitle", lang)}</p>
            
            <div style="text-align: center; margin-bottom: var(--space-12);">
                <span style="background: var(--gradient-accent); color: white; padding: var(--space-2) var(--space-6); border-radius: var(--radius-pill); font-weight: 600;">
                    {len(modules)} {t("modules_count", lang)}
                </span>
            </div>
            
            <div class="core-values-grid">
                {modules_html}
            </div>
        </div>
        
        {render_footer(lang)}
    </body>
    </html>
    """
