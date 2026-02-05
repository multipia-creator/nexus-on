/**
 * i18n Translations for NEXUS-ON Marketing Pages
 * Ported from backend/nexus_supervisor/public_pages_i18n.py
 */

export type Language = 'ko' | 'en'

export interface Translations {
  [key: string]: string
}

export const translations: Record<Language, Translations> = {
  ko: {
    // Navigation
    nav_home: '홈',
    nav_intro: '소개',
    nav_modules: '모듈',
    nav_pricing: '가격',
    nav_dashboard: '대시보드',
    nav_canvas: '캔버스',
    nav_login: '로그인',
    
    // Hero Section
    hero_input_placeholder: '무엇을 도와드릴까요?',
    hero_voice_button: '음성 입력',
    hero_text_button: '전송',
    voice_not_supported: '이 브라우저는 음성 인식을 지원하지 않습니다.',
    hero_title: '잠들지 않는<br>당신만의 AI 캐릭터 비서',
    hero_subtitle: '항상 깨어있는 당신만의 AI 캐릭터 비서',
    hero_tagline: 'Live2D 캐릭터가 화면에 항상 존재하며, 자율적으로 작업을 수행하지만<br>중요한 결정은 항상 당신의 승인을 받습니다.',
    hero_cta_primary: '무료로 시작하기',
    hero_cta_secondary: '데모 보기',
    
    // Core Values
    value1_title: '항상 화면에 존재',
    value1_desc: '화면에 항상 존재하는 Live2D 캐릭터 비서.<br>5가지 상태로 현재 작업을 시각적으로 표현합니다.',
    value2_title: '자율적이지만 통제 가능',
    value2_desc: '자율적으로 작업을 수행하지만,<br>중요한 결정은 항상 당신의 승인을 받습니다.',
    value3_title: '한국어 네이티브',
    value3_desc: '한국어 네이티브 지원.<br>HWP 파일을 완벽하게 처리합니다.',
    
    // Footer
    footer_text: '잠들지 않는 당신만의 AI 캐릭터 비서',
    footer_dev: '개발: 남현우 교수, 서경대학교 VD_비주얼디자인전공',
    
    // Intro Page
    intro_title: 'NEXUS-ON 소개',
    intro_subtitle: 'Live2D 캐릭터 비서 기반의 자율 AI 에이전트 시스템',
    intro_worldclass_title: '세계 최고 수준의 AI 비서',
    intro_worldclass_subtitle: 'NEXUS-ON이 다른 AI 비서와 차별화되는 이유',
    intro_feature1_title: '🎭 Live2D 캐릭터 비서',
    intro_feature1_content: '단순한 챗봇이 아닙니다. 화면에 항상 존재하는 Live2D 캐릭터가 5가지 상태(Idle, Listening, Thinking, Speaking, Busy)로 현재 작업을 시각적으로 표현합니다. Haru 모델 기반으로 실시간 애니메이션과 립싱크를 지원합니다.',
    intro_feature2_title: '🛡️ Human-in-the-loop 승인 시스템',
    intro_feature2_content: 'ShieldCheck 시스템이 모든 작업을 위험도에 따라 GREEN/YELLOW/RED로 분류합니다. 파일 삭제나 외부 공유 같은 위험한 작업은 반드시 사용자 승인이 필요하며, Two-phase commit 프로토콜로 안전성을 보장합니다.',
    intro_feature3_title: '📚 한국어 네이티브 지원',
    intro_feature3_content: 'HWP(한글 파일)을 외부 변환 없이 직접 처리하는 FileSearch 엔진을 탑재했습니다. Token overlap 기반 RAG로 한국어 학술 워크플로우에 최적화되어 있으며, 매일 03:00 KST에 자동으로 문서를 색인합니다.',
    intro_feature4_title: '🔄 멀티 에이전트 오케스트레이션',
    intro_feature4_content: '8개의 전문화된 모듈(Bot, ShieldCheck, FileSearch, Youtube, FileEdit, Users, MonitorCheck, Activity)이 협업하여 복잡한 작업을 자동으로 수행합니다. Claude Sonnet 4.5 기반으로 멀티스텝 작업을 지능적으로 처리합니다.',
    intro_feature5_title: '🏠 Local-first 아키텍처',
    intro_feature5_content: '모든 데이터는 로컬에서 처리되며 클라우드 업로드 없이 안전합니다. Multi-tenant 지원으로 조직 단위 배포가 가능하며, org-id 및 project-id 기반 격리로 데이터 유출을 원천 차단합니다.',
    intro_feature6_title: '🎯 실시간 작업 모니터링',
    intro_feature6_content: 'SSE(Server-Sent Events)를 통해 세리아의 모든 행동을 실시간으로 추적합니다. Live2D 캐릭터가 작업 상태를 즉시 반영하며, RED 작업 시 Alert glow(빨간 테두리)로 승인 대기를 시각화합니다.',
    
    // Modules Page
    modules_title: '모듈 시스템',
    modules_subtitle: '8개의 핵심 모듈로 구성된 강력한 AI 에이전트',
    modules_count: '개 모듈',
    
    module_bot_title: 'Bot',
    module_bot_subtitle: 'Character Assistant Core',
    module_bot_desc: 'Live2D 캐릭터 + Claude Sonnet 4.5 대화형 에이전트. NEXUS의 심장부로, 4가지 애니메이션 상태를 통해 시각적 피드백을 제공하며 멀티턴 컨텍스트를 유지합니다.',
    module_bot_status: 'Production Ready',
    
    module_shield_title: 'ShieldCheck',
    module_shield_subtitle: 'Human-in-the-loop Approval System',
    module_shield_desc: '위험 기반 승인 워크플로우 (GREEN/YELLOW/RED). 자동 실행, 알림, 명시적 승인의 3단계 게이트로 NEXUS가 무분별하게 행동하지 않도록 보호합니다.',
    module_shield_status: 'Production Ready',
    
    module_filesearch_title: 'FileSearch',
    module_filesearch_subtitle: 'RAG Engine (Token Overlap)',
    module_filesearch_desc: 'Token overlap 기반 검색으로 한국어 HWP 네이티브 지원. RAG 엔진은 한국어 학술 워크플로우에 최적화되어 있으며, 매일 03:00 KST 자동 색인으로 증거 추적이 가능합니다.',
    module_filesearch_status: 'Beta - Active Development',
    
    module_youtube_title: 'Youtube',
    module_youtube_subtitle: 'YouTube Integration',
    module_youtube_desc: '연구 및 학습 워크플로우를 위한 완전한 YouTube 통합. YouTube Data API v3로 검색, 큐 관리, 내장 플레이어를 지원하며 Live2D 캐릭터가 Speaking 상태로 비디오 콘텐츠를 설명합니다.',
    module_youtube_status: 'Production Ready',
    
    module_fileedit_title: 'FileEdit',
    module_fileedit_subtitle: 'Canvas Workspace',
    module_fileedit_desc: '멀티포맷 내보내기를 지원하는 협업 워크스페이스. 로컬 draft 저장소(서버 업로드 없음)로 문서를 작성하고 편집하며, Live2D 캐릭터가 Thinking 상태로 긴 draft 작업 시 표시됩니다.',
    module_fileedit_status: 'Beta - Under Refinement',
    
    module_users_title: 'Users',
    module_users_subtitle: 'Multi-tenant Context',
    module_users_desc: '팀 배포를 위한 엔터프라이즈급 멀티테넌시. org-id 및 project-id로 범위를 지정하며, 테넌트별 API 키로 자격 증명을 격리합니다. 비용 태깅과 감사 추적으로 완전한 책임성을 보장합니다.',
    module_users_status: 'Production Ready',
    
    module_monitor_title: 'MonitorCheck',
    module_monitor_subtitle: 'Windows Agent',
    module_monitor_desc: 'Windows 환경 모니터링 에이전트 (베타). 시스템 상태를 추적하고 Live2D 캐릭터와 통합하여 시스템 이벤트를 실시간으로 보고합니다.',
    module_monitor_status: 'Beta - Windows Agent',
    
    module_activity_title: 'Activity',
    module_activity_subtitle: 'Activity Metrics',
    module_activity_desc: '알파 단계의 활동 메트릭 추적 시스템. 세리아의 모든 행동을 로깅하고 분석하여 사용 패턴과 효율성을 측정합니다.',
    module_activity_status: 'Alpha - Metrics Only',
    
    // Developer Profile
    developer_title: '개발자 소개',
    developer_name: '남현우 교수',
    developer_affiliation: '서경대학교 디자인학부 VD_비주얼디자인전공 콘텐츠시스템',
    developer_specialty: 'AI, Blockchain, IoT, XR',
    developer_website: 'DXPIA.com',
    developer_research_title: '연구 분야',
    developer_research_1: 'ICT 전략 & 콘텐츠 시스템 디자인',
    developer_research_2: 'AI 에이전트 시스템 및 Human-in-the-loop 인터페이스',
    developer_research_3: 'Blockchain 기반 ART NFT 플랫폼',
    developer_research_4: 'IoT 기반 뷰티 AI 서비스 시스템',
    developer_research_5: 'XR(VR/AR/MR) 및 메타버스 콘텐츠 전략',
    developer_vision_title: '프로젝트 비전',
    developer_vision_content: 'NEXUS-ON은 인간-AI 협업의 새로운 패러다임을 제시합니다. Local-first 아키텍처로 데이터 안전을 보장하고, HWP를 포함한 한국어 문서를 완벽하게 처리하며, 항상 사용자의 통제 하에서 작동하는 투명하고 신뢰할 수 있는 AI 비서를 목표로 합니다.',
    developer_philosophy_title: '개발 철학',
    developer_philosophy_1: 'Local-first: 클라우드 업로드 없는 안전한 데이터 처리',
    developer_philosophy_2: 'Human oversight: 중요한 결정은 항상 사용자 승인',
    developer_philosophy_3: 'Fail-safe: 오류 발생 시 안전한 기본 상태로 복귀',
    developer_philosophy_4: 'Open by design: 교육 및 연구를 위한 오픈소스 프로젝트',
    developer_contact_title: '연락처',
    developer_contact_dept: '서경대학교 디자인학부 VD_비주얼디자인전공',
    developer_contact_lab: '콘텐츠시스템 Lab (AI, Blockchain, IoT, XR)',
    developer_contact_website: 'DXPIA.com',
    developer_contact_project: 'NEXUS-ON 오픈소스 프로젝트',
    
    // Pricing Page
    pricing_title: '가격 플랜',
    pricing_subtitle: '당신의 필요에 맞는 플랜을 선택하세요.<br>언제든지 업그레이드 가능합니다.',
    pricing_free_title: 'FREE',
    pricing_free_price: '₩0',
    pricing_free_period: '영원히 무료',
    pricing_plus_title: 'PLUS',
    pricing_plus_price: '₩29,000',
    pricing_plus_period: '/월',
    pricing_plus_badge: '인기',
    pricing_pro_title: 'PRO',
    pricing_pro_price: '₩99,000',
    pricing_pro_period: '/월',
    pricing_pro_badge: '추천',
  },
  en: {
    // Navigation
    nav_home: 'Home',
    nav_intro: 'About',
    nav_modules: 'Modules',
    nav_pricing: 'Pricing',
    nav_dashboard: 'Dashboard',
    nav_canvas: 'Canvas',
    nav_login: 'Login',
    
    // Hero Section
    hero_input_placeholder: 'What can I help you with?',
    hero_voice_button: 'Voice Input',
    hero_text_button: 'Send',
    voice_not_supported: 'Your browser does not support speech recognition.',
    hero_title: 'Your AI Character Assistant<br>That Never Sleeps',
    hero_subtitle: 'Your Always-On AI Character Assistant',
    hero_tagline: 'A Live2D character is always present on your screen, working autonomously<br>but always seeking your approval for important decisions.',
    hero_cta_primary: 'Start Free',
    hero_cta_secondary: 'Watch Demo',
    
    // Core Values
    value1_title: 'Always Visible',
    value1_desc: 'A Live2D character assistant always present on screen.<br>5 states visually represent current tasks.',
    value2_title: 'Autonomous but Controlled',
    value2_desc: 'Works autonomously,<br>but always requires your approval for critical decisions.',
    value3_title: 'Korean Native',
    value3_desc: 'Native Korean language support.<br>Handles HWP files perfectly.',
    
    // Footer
    footer_text: 'Your AI Character Assistant That Never Sleeps',
    footer_dev: 'Developed by Prof. Nam Hyunwoo, Seokyeong University VD_Visual Design',
    
    // Intro Page
    intro_title: 'About NEXUS-ON',
    intro_subtitle: 'Autonomous AI Agent System with Live2D Character Assistant',
    intro_worldclass_title: 'World-Class AI Assistant',
    intro_worldclass_subtitle: 'What makes NEXUS-ON different from other AI assistants',
    intro_feature1_title: '🎭 Live2D Character Assistant',
    intro_feature1_content: 'Not just a chatbot. A Live2D character always present on screen displays current tasks through 5 states (Idle, Listening, Thinking, Speaking, Busy). Based on Haru model with real-time animation and lip-sync support.',
    intro_feature2_title: '🛡️ Human-in-the-loop Approval System',
    intro_feature2_content: 'ShieldCheck system classifies all tasks by risk level: GREEN/YELLOW/RED. Dangerous operations like file deletion or external sharing require user approval, with Two-phase commit protocol ensuring safety.',
    intro_feature3_title: '📚 Native Korean Support',
    intro_feature3_content: 'FileSearch engine processes HWP (Hangul files) directly without external conversion. Token overlap-based RAG optimized for Korean academic workflows, with automatic indexing at 03:00 KST daily.',
    intro_feature4_title: '🔄 Multi-Agent Orchestration',
    intro_feature4_content: '8 specialized modules (Bot, ShieldCheck, FileSearch, Youtube, FileEdit, Users, MonitorCheck, Activity) collaborate to automatically handle complex tasks. Claude Sonnet 4.5-based intelligent multi-step processing.',
    intro_feature5_title: '🏠 Local-first Architecture',
    intro_feature5_content: 'All data processed locally, safe without cloud uploads. Multi-tenant support enables organization-wide deployment, with org-id and project-id-based isolation preventing data leaks.',
    intro_feature6_title: '🎯 Real-time Task Monitoring',
    intro_feature6_content: "Track all of Ceria's actions in real-time via SSE (Server-Sent Events). Live2D character immediately reflects task status, with Alert glow (red border) visualizing approval pending for RED tasks.",
    
    // Modules Page
    modules_title: 'Module System',
    modules_subtitle: 'Powerful AI agent composed of 8 core modules',
    modules_count: ' modules',
    
    module_bot_title: 'Bot',
    module_bot_subtitle: 'Character Assistant Core',
    module_bot_desc: 'Live2D character + Claude Sonnet 4.5 conversational agent. The heart of NEXUS, providing visual feedback through 4 animation states and maintaining multi-turn context.',
    module_bot_status: 'Production Ready',
    
    module_shield_title: 'ShieldCheck',
    module_shield_subtitle: 'Human-in-the-loop Approval System',
    module_shield_desc: 'Risk-based approval workflow (GREEN/YELLOW/RED). 3-tier gate of auto-execute, notify, and explicit approval protects NEXUS from acting recklessly.',
    module_shield_status: 'Production Ready',
    
    module_filesearch_title: 'FileSearch',
    module_filesearch_subtitle: 'RAG Engine (Token Overlap)',
    module_filesearch_desc: 'Token overlap-based search with native Korean HWP support. RAG engine optimized for Korean academic workflows, with automatic indexing at 03:00 KST daily for evidence tracking.',
    module_filesearch_status: 'Beta - Active Development',
    
    module_youtube_title: 'Youtube',
    module_youtube_subtitle: 'YouTube Integration',
    module_youtube_desc: 'Full YouTube integration for research and learning workflows. YouTube Data API v3 supports search, queue management, and embedded player, with Live2D character explaining video content in Speaking state.',
    module_youtube_status: 'Production Ready',
    
    module_fileedit_title: 'FileEdit',
    module_fileedit_subtitle: 'Canvas Workspace',
    module_fileedit_desc: 'Collaborative workspace with multi-format export support. Create and edit documents in local draft repository (no server upload), with Live2D character displaying in Thinking state during long draft work.',
    module_fileedit_status: 'Beta - Under Refinement',
    
    module_users_title: 'Users',
    module_users_subtitle: 'Multi-tenant Context',
    module_users_desc: 'Enterprise-grade multitenancy for team deployment. Scoped by org-id and project-id, with per-tenant API keys isolating credentials. Cost tagging and audit trails ensure complete accountability.',
    module_users_status: 'Production Ready',
    
    module_monitor_title: 'MonitorCheck',
    module_monitor_subtitle: 'Windows Agent',
    module_monitor_desc: 'Windows environment monitoring agent (beta). Tracks system status and integrates with Live2D character to report system events in real-time.',
    module_monitor_status: 'Beta - Windows Agent',
    
    module_activity_title: 'Activity',
    module_activity_subtitle: 'Activity Metrics',
    module_activity_desc: "Alpha-stage activity metrics tracking system. Logs and analyzes all of Ceria's actions to measure usage patterns and efficiency.",
    module_activity_status: 'Alpha - Metrics Only',
    
    // Developer Profile
    developer_title: 'Developer Profile',
    developer_name: 'Professor Nam Hyunwoo',
    developer_affiliation: 'Seokyeong University, Visual Design Major, Content System',
    developer_specialty: 'AI, Blockchain, IoT, XR',
    developer_website: 'DXPIA.com',
    developer_research_title: 'Research Areas',
    developer_research_1: 'ICT Strategy & Content System Design',
    developer_research_2: 'AI Agent Systems & Human-in-the-loop Interfaces',
    developer_research_3: 'Blockchain-based ART NFT Platform',
    developer_research_4: 'IoT-based Beauty AI Service System',
    developer_research_5: 'XR (VR/AR/MR) & Metaverse Content Strategy',
    developer_vision_title: 'Project Vision',
    developer_vision_content: 'NEXUS-ON presents a new paradigm of human-AI collaboration. With local-first architecture ensuring data safety, perfect processing of Korean documents including HWP, and transparent, trustworthy AI assistant operating always under user control.',
    developer_philosophy_title: 'Development Philosophy',
    developer_philosophy_1: 'Local-first: Secure data processing without cloud uploads',
    developer_philosophy_2: 'Human oversight: Important decisions always require user approval',
    developer_philosophy_3: 'Fail-safe: Return to safe default state on errors',
    developer_philosophy_4: 'Open by design: Open-source project for education and research',
    developer_contact_title: 'Contact',
    developer_contact_dept: 'Seokyeong University, Visual Design Major',
    developer_contact_lab: 'Content System Lab (AI, Blockchain, IoT, XR)',
    developer_contact_website: 'DXPIA.com',
    developer_contact_project: 'NEXUS-ON Open Source Project',
    
    // Pricing Page
    pricing_title: 'Pricing Plans',
    pricing_subtitle: 'Choose the plan that fits your needs.<br>Upgrade anytime.',
    pricing_free_title: 'FREE',
    pricing_free_price: '₩0',
    pricing_free_period: 'Forever Free',
    pricing_plus_title: 'PLUS',
    pricing_plus_price: '₩29,000',
    pricing_plus_period: '/month',
    pricing_plus_badge: 'Popular',
    pricing_pro_title: 'PRO',
    pricing_pro_price: '₩99,000',
    pricing_pro_period: '/month',
    pricing_pro_badge: 'Recommended',
  }
}

/**
 * Get translation for given key and language
 */
export function t(key: string, lang: Language = 'ko'): string {
  return translations[lang][key] || key
}
