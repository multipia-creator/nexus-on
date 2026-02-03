/**
 * NEXUS 프로젝트 환경 변수 타입 정의
 * Cloudflare Workers/Pages에서 사용하는 환경 변수 및 바인딩
 */

export type Bindings = {
  // API Keys
  CLOUDFLARE_API_TOKEN: string
  GITHUB_TOKEN: string
  GOOGLE_API_KEY: string
  OPENAI_API_KEY: string
  OPENROUTER_API_KEY: string

  // Cloudflare Services (추후 추가 시)
  // DB?: D1Database
  // KV?: KVNamespace
  // R2?: R2Bucket
}

// Hono Context 타입
export type HonoEnv = {
  Bindings: Bindings
}
