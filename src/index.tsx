import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { serveStatic } from 'hono/cloudflare-workers'
import { renderer } from './renderer'
import type { HonoEnv } from './types'

const app = new Hono<HonoEnv>()

// Backend API URL (환경변수 또는 기본값)
const BACKEND_URL = 'https://8000-izouutirnrjsk0u0z191s-d0b9e1e2.sandbox.novita.ai'

// CORS 설정 (API 엔드포인트용)
app.use('/api/*', cors())

// Static 파일 서빙
app.use('/static/*', serveStatic({ root: './public' }))
app.use('/live2d/*', serveStatic({ root: './public' }))

// Backend 페이지 프록시 (마케팅 사이트)
const proxyToBackend = async (c: any) => {
  const url = new URL(c.req.url)
  const backendUrl = `${BACKEND_URL}${url.pathname}${url.search}`
  
  try {
    const response = await fetch(backendUrl, {
      method: c.req.method,
      headers: {
        'User-Agent': 'NEXUS-Frontend-Proxy/1.0'
      }
    })
    
    const contentType = response.headers.get('content-type') || ''
    const body = contentType.includes('application/json') 
      ? await response.json()
      : await response.text()
    
    return new Response(typeof body === 'string' ? body : JSON.stringify(body), {
      status: response.status,
      headers: {
        'Content-Type': contentType
      }
    })
  } catch (error) {
    return c.html(
      `<html><body>
        <h1>Backend Unavailable</h1>
        <p>Unable to connect to backend server.</p>
        <p>Error: ${String(error)}</p>
      </body></html>`,
      503
    )
  }
}

// 마케팅 페이지 라우트 (Backend로 프록시)
app.get('/', proxyToBackend)
app.get('/intro', proxyToBackend)
app.get('/developer', proxyToBackend)
app.get('/modules', proxyToBackend)
app.get('/pricing', proxyToBackend)
app.get('/dashboard-preview', proxyToBackend)
app.get('/canvas-preview', proxyToBackend)
app.get('/login', proxyToBackend)
app.get('/live2d-test', proxyToBackend)

// Backend API 엔드포인트 프록시
app.all('/api/*', async (c) => {
  const url = new URL(c.req.url)
  const backendUrl = `${BACKEND_URL}${url.pathname}${url.search}`
  
  try {
    const body = c.req.method !== 'GET' && c.req.method !== 'HEAD' 
      ? await c.req.text() 
      : undefined
    
    const response = await fetch(backendUrl, {
      method: c.req.method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'NEXUS-Frontend-Proxy/1.0'
      },
      body
    })
    
    const data = await response.json()
    return c.json(data, response.status)
  } catch (error) {
    return c.json({ 
      error: 'Backend API unavailable',
      message: String(error)
    }, 503)
  }
})

// TTS 파일 서빙 프록시
app.get('/tts/:filename', proxyToBackend)

// Health check (Frontend 자체)
app.get('/health', (c) => {
  return c.json({
    status: 'ok',
    service: 'NEXUS-Frontend',
    backend: BACKEND_URL,
    timestamp: new Date().toISOString()
  })
})

export default app
