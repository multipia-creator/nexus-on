/**
 * NEXUS-ON Cloudflare MSA - Shared Types
 */

export type Language = 'ko' | 'en'

export type Live2DState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'busy'

export interface CloudflareEnv {
  DB?: D1Database
  KV?: KVNamespace
  R2?: R2Bucket
  ELEVENLABS_API_KEY?: string
}

export interface ModuleData {
  name: string
  title: string
  subtitle: string
  desc: string
  status: string
  icon?: string
}
