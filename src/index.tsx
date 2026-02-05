import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { serveStatic } from 'hono/cloudflare-workers'
import type { HonoEnv } from './types'
import { 
  renderLandingPage, 
  renderIntroPage, 
  renderDeveloperPage, 
  renderModulesPage 
} from './pages'
import type { Language } from './i18n'

const app = new Hono<HonoEnv>()

// CORS 설정 (API 엔드포인트용)
app.use('/api/*', cors())

// Static 파일 서빙
app.use('/static/*', serveStatic({ root: './public' }))
app.use('/live2d/*', serveStatic({ root: './public' }))

// Helper: Get language from query param
function getLang(c: any): Language {
  const lang = c.req.query('lang')
  return lang === 'en' ? 'en' : 'ko'
}

// 마케팅 페이지 라우트 (직접 렌더링)
app.get('/', (c) => {
  return c.html(renderLandingPage(getLang(c)))
})

app.get('/intro', (c) => {
  return c.html(renderIntroPage(getLang(c)))
})

app.get('/developer', (c) => {
  return c.html(renderDeveloperPage(getLang(c)))
})

app.get('/modules', (c) => {
  return c.html(renderModulesPage(getLang(c)))
})

// Placeholder pages
app.get('/pricing', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>Pricing - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; text-align: center;">
      <h1>💰 Pricing Page</h1>
      <p>Coming soon...</p>
      <a href="/?lang=${lang}">← Back to Home</a>
    </body>
    </html>
  `)
})

app.get('/dashboard-preview', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>Dashboard - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; text-align: center;">
      <h1>📊 Dashboard Preview</h1>
      <p>Coming soon...</p>
      <a href="/?lang=${lang}">← Back to Home</a>
    </body>
    </html>
  `)
})

app.get('/canvas-preview', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>Canvas - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; text-align: center;">
      <h1>🎨 Canvas Workspace</h1>
      <p>Coming soon...</p>
      <a href="/?lang=${lang}">← Back to Home</a>
    </body>
    </html>
  `)
})

app.get('/login', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>Login - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; text-align: center;">
      <h1>🔐 Login</h1>
      <p>Coming soon...</p>
      <a href="/?lang=${lang}">← Back to Home</a>
    </body>
    </html>
  `)
})

app.get('/live2d-test', (c) => {
  const lang = getLang(c)
  return c.html(`
    <!DOCTYPE html>
    <html>
    <head><title>Live2D Test - NEXUS-ON</title></head>
    <body style="font-family: sans-serif; padding: 40px; text-align: center;">
      <h1>🎭 Live2D Test Page</h1>
      <p>Live2D integration coming soon...</p>
      <a href="/?lang=${lang}">← Back to Home</a>
    </body>
    </html>
  `)
})

// Health check
app.get('/health', (c) => {
  return c.json({
    status: 'ok',
    service: 'NEXUS-Frontend',
    version: '2.0.0',
    timestamp: new Date().toISOString()
  })
})

export default app
