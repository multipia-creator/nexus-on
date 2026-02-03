import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { renderer } from './renderer'
import type { HonoEnv } from './types'

const app = new Hono<HonoEnv>()

// CORS 설정 (API 엔드포인트용)
app.use('/api/*', cors())

// 렌더러 설정
app.use(renderer)

// 메인 페이지
app.get('/', (c) => {
  return c.render(
    <div>
      <h1>NEXUS - 세리아 AI 에이전트 시스템</h1>
      <p>차세대 AI 에이전트 시스템에 오신 것을 환영합니다.</p>
    </div>
  )
})

// API 상태 체크
app.get('/api/status', (c) => {
  return c.json({
    status: 'ok',
    project: 'NEXUS',
    version: '0.1.0',
    timestamp: new Date().toISOString()
  })
})

// API 키 테스트 엔드포인트 (환경 변수 확인용)
app.get('/api/keys/check', (c) => {
  const { env } = c
  
  return c.json({
    cloudflare: env.CLOUDFLARE_API_TOKEN ? '✅ 설정됨' : '❌ 미설정',
    github: env.GITHUB_TOKEN ? '✅ 설정됨' : '❌ 미설정',
    google: env.GOOGLE_API_KEY ? '✅ 설정됨' : '❌ 미설정',
    openai: env.OPENAI_API_KEY ? '✅ 설정됨' : '❌ 미설정',
    openrouter: env.OPENROUTER_API_KEY ? '✅ 설정됨' : '❌ 미설정'
  })
})

// OpenAI API 프록시 예제
app.post('/api/chat/openai', async (c) => {
  const { env } = c
  
  if (!env.OPENAI_API_KEY) {
    return c.json({ error: 'OpenAI API key not configured' }, 500)
  }
  
  try {
    const body = await c.req.json()
    
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: body.model || 'gpt-4',
        messages: body.messages || [{ role: 'user', content: 'Hello!' }],
        max_tokens: body.max_tokens || 1000
      })
    })
    
    if (!response.ok) {
      const error = await response.json()
      return c.json({ error: 'OpenAI API error', details: error }, response.status)
    }
    
    const data = await response.json()
    return c.json(data)
  } catch (error) {
    return c.json({ error: 'Failed to call OpenAI API', message: String(error) }, 500)
  }
})

// OpenRouter API 프록시 예제
app.post('/api/chat/openrouter', async (c) => {
  const { env } = c
  
  if (!env.OPENROUTER_API_KEY) {
    return c.json({ error: 'OpenRouter API key not configured' }, 500)
  }
  
  try {
    const body = await c.req.json()
    
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://nexus.pages.dev',
        'X-Title': 'NEXUS AI Agent'
      },
      body: JSON.stringify({
        model: body.model || 'anthropic/claude-3-opus',
        messages: body.messages || [{ role: 'user', content: 'Hello!' }]
      })
    })
    
    if (!response.ok) {
      const error = await response.json()
      return c.json({ error: 'OpenRouter API error', details: error }, response.status)
    }
    
    const data = await response.json()
    return c.json(data)
  } catch (error) {
    return c.json({ error: 'Failed to call OpenRouter API', message: String(error) }, 500)
  }
})

export default app
