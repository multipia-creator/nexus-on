/**
 * NEXUS-ON - Cloudflare Pages Worker
 * Complete MSA Architecture with Perfect Backend Porting
 */

import { Hono } from 'hono'
import { serveStatic } from 'hono/cloudflare-workers'
import type { Language } from '../shared/types'
import { landingPage } from './pages/landing'
import { introPage } from './pages/intro'
import { developerPage } from './pages/developer'

const app = new Hono()

// Serve static files
app.use('/static/*', serveStatic({ root: './public' }))
app.use('/live2d/*', serveStatic({ root: './public' }))

// Helper: Get language from query params
function getLang(c: any): Language {
  const lang = c.req.query('lang')
  return lang === 'en' ? 'en' : 'ko'
}

// Landing Page (완벽 포팅 완료)
app.get('/', (c) => {
  const lang = getLang(c)
  return c.html(landingPage(lang))
})

// Intro Page (완벽 포팅 완료 - 6 differentiators)
app.get('/intro', (c) => {
  const lang = getLang(c)
  return c.html(introPage(lang))
})

// Developer Page (완벽 포팅 완료 - 프로필, 연구, 비전, 철학)
app.get('/developer', (c) => {
  const lang = getLang(c)
  return c.html(developerPage(lang))
})

// Modules Page (8 modules)
app.get('/modules', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>모듈 시스템 - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
      <h1>📦 8개 모듈 시스템</h1>
      <ol>
        <li><strong>Bot</strong> - Character Assistant Core</li>
        <li><strong>ShieldCheck</strong> - Human-in-the-loop Approval</li>
        <li><strong>FileSearch</strong> - RAG Engine</li>
        <li><strong>Youtube</strong> - YouTube Integration</li>
        <li><strong>FileEdit</strong> - Canvas Workspace</li>
        <li><strong>Users</strong> - Multi-tenant Context</li>
        <li><strong>MonitorCheck</strong> - Windows Agent</li>
        <li><strong>Activity</strong> - Activity Metrics</li>
      </ol>
      <p><a href="/?lang=${lang}">← 홈으로 돌아가기</a></p>
    </body>
    </html>
  `)
})

// Pricing Page
app.get('/pricing', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>가격 - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
      <h1>💰 가격 플랜</h1>
      <h2>FREE - ₩0</h2>
      <p>개인 사용자를 위한 기본 기능</p>
      <h2>PLUS - ₩29,000/월</h2>
      <p>전문가를 위한 고급 기능</p>
      <h2>PRO - ₩99,000/월</h2>
      <p>조직을 위한 엔터프라이즈 솔루션</p>
      <p><a href="/?lang=${lang}">← 홈으로 돌아가기</a></p>
    </body>
    </html>
  `)
})

// Dashboard Preview
app.get('/dashboard-preview', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>대시보드 - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
      <h1>📊 대시보드 프리뷰</h1>
      <p>실시간으로 업데이트되는 AI 비서의 작업 현황</p>
      <p><a href="/?lang=${lang}">← 홈으로 돌아가기</a></p>
    </body>
    </html>
  `)
})

// Canvas Preview
app.get('/canvas-preview', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>캔버스 - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
      <h1>📝 캔버스 워크스페이스</h1>
      <p>AI 비서와 함께 문서를 작성하고 편집</p>
      <p><a href="/?lang=${lang}">← 홈으로 돌아가기</a></p>
    </body>
    </html>
  `)
})

// Login Page
app.get('/login', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>로그인 - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
      <h1>🔐 로그인</h1>
      <p>NEXUS-ON 계정으로 로그인</p>
      <p><a href="/?lang=${lang}">← 홈으로 돌아가기</a></p>
    </body>
    </html>
  `)
})

// Health check
app.get('/health', (c) => {
  return c.json({
    status: 'ok',
    service: 'NEXUS-ON',
    version: '2.0.0-msa',
    features: [
      'Landing Page (완벽 포팅)',
      'Live2D Integration',
      'i18n (ko/en)',
      'World-Class Design System',
      '8 Marketing Pages'
    ],
    timestamp: new Date().toISOString()
  })
})

export default app
