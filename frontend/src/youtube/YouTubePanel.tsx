import { useState } from 'react'
import type { YouTubeVideo, YouTubeQueueItem } from './types'
import { postJSON } from '../lib/http'

type Props = {
  baseUrl: string
  orgId: string
  projectId: string
  sessionId: string
  apiKey: string
  demoMode?: boolean
}

export function YouTubePanel(p: Props) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<YouTubeVideo[]>([])
  const [queue, setQueue] = useState<YouTubeQueueItem[]>([])
  const [currentVideo, setCurrentVideo] = useState<YouTubeQueueItem | null>(null)
  const [searching, setSearching] = useState(false)
  const [loading, setLoading] = useState(false)

  const headers = {
    'x-org-id': p.orgId,
    'x-project-id': p.projectId,
    'x-api-key': p.apiKey
  }

  async function handleSearch() {
    if (!query.trim() || searching) return
    
    if (p.demoMode) {
      setResults([
        {
          video_id: 'demo-vid-1',
          title: '[데모] NEXUS Tutorial - Getting Started',
          channel_title: 'NEXUS Official',
          thumbnail: 'https://via.placeholder.com/320x180?text=Demo+Video',
          duration_sec: 300,
          view_count: 12345,
          link: 'https://www.youtube.com/watch?v=demo-vid-1',
          published_at: new Date().toISOString(),
          fetched_at: new Date().toISOString()
        }
      ])
      return
    }

    setSearching(true)
    try {
      await postJSON(
        `${p.baseUrl}/sidecar/command`,
        {
          command_id: `cmd-yt-search-${Date.now()}`,
          type: 'youtube.search',
          params: { query: query.trim(), max_results: 6 },
          client_context: { session_id: p.sessionId, correlation_id: `corr-yt-${Date.now()}` }
        },
        headers
      )
      // Results will come via SSE
    } catch (err) {
      console.error('YouTube search failed:', err)
      alert('검색 실패. 다시 시도해주세요.')
    } finally {
      setSearching(false)
    }
  }

  async function handleAddToQueue(video: YouTubeVideo) {
    if (loading) return
    
    if (p.demoMode) {
      const item: YouTubeQueueItem = {
        video_id: video.video_id,
        title: video.title,
        channel: video.channel_title,
        embed_url: `https://www.youtube.com/embed/${video.video_id}`,
        added_at: new Date().toISOString()
      }
      setQueue([...queue, item])
      return
    }

    setLoading(true)
    try {
      await postJSON(
        `${p.baseUrl}/sidecar/command`,
        {
          command_id: `cmd-yt-queue-add-${Date.now()}`,
          type: 'youtube.queue.add',
          params: {
            video_id: video.video_id,
            title: video.title,
            channel: video.channel_title
          },
          client_context: { session_id: p.sessionId, correlation_id: `corr-ytq-${Date.now()}` }
        },
        headers
      )
      // Queue update will come via SSE
    } catch (err) {
      console.error('Add to queue failed:', err)
      alert('큐 추가 실패. 다시 시도해주세요.')
    } finally {
      setLoading(false)
    }
  }

  async function handlePlayNext() {
    if (loading || queue.length === 0) return
    
    if (p.demoMode) {
      const next = queue[0]
      setCurrentVideo(next)
      setQueue(queue.slice(1))
      return
    }

    setLoading(true)
    try {
      await postJSON(
        `${p.baseUrl}/sidecar/command`,
        {
          command_id: `cmd-yt-queue-next-${Date.now()}`,
          type: 'youtube.queue.next',
          params: {},
          client_context: { session_id: p.sessionId, correlation_id: `corr-ytq-next-${Date.now()}` }
        },
        headers
      )
      // Next video will come via SSE
    } catch (err) {
      console.error('Play next failed:', err)
      alert('재생 실패. 다시 시도해주세요.')
    } finally {
      setLoading(false)
    }
  }

  async function handleClearQueue() {
    if (loading) return
    
    if (p.demoMode) {
      setQueue([])
      return
    }

    setLoading(true)
    try {
      await postJSON(
        `${p.baseUrl}/sidecar/command`,
        {
          command_id: `cmd-yt-queue-clear-${Date.now()}`,
          type: 'youtube.queue.clear',
          params: {},
          client_context: { session_id: p.sessionId, correlation_id: `corr-ytq-clear-${Date.now()}` }
        },
        headers
      )
      setQueue([])
    } catch (err) {
      console.error('Clear queue failed:', err)
      alert('큐 초기화 실패. 다시 시도해주세요.')
    } finally {
      setLoading(false)
    }
  }

  function formatDuration(sec: number | null): string {
    if (!sec) return '-'
    const m = Math.floor(sec / 60)
    const s = sec % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  function formatViews(count: number | null): string {
    if (!count) return '0'
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`
    return count.toString()
  }

  return (
    <div className="ytPanel">
      {/* 검색 */}
      <div className="ytSearch">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter') handleSearch()
          }}
          placeholder="YouTube 검색..."
          disabled={searching}
        />
        <button onClick={handleSearch} disabled={searching || !query.trim()}>
          {searching ? '검색 중...' : '검색'}
        </button>
      </div>

      {/* Player */}
      {currentVideo && (
        <div className="ytPlayer">
          <h3>재생 중</h3>
          <div className="ytPlayerTitle">{currentVideo.title}</div>
          <div className="ytPlayerChannel">{currentVideo.channel}</div>
          <iframe
            src={currentVideo.embed_url}
            title={currentVideo.title}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      {/* 검색 결과 */}
      {results.length > 0 && (
        <div className="ytResults">
          <h3>검색 결과</h3>
          <div className="ytList">
            {results.map(video => (
              <div key={video.video_id} className="ytItem">
                <img src={video.thumbnail} alt={video.title} />
                <div className="ytItemBody">
                  <div className="ytItemTitle">{video.title}</div>
                  <div className="ytItemMeta">
                    <span>{video.channel_title}</span>
                    <span>{formatViews(video.view_count)} views</span>
                    <span>{formatDuration(video.duration_sec)}</span>
                  </div>
                </div>
                <button
                  className="btn primary"
                  onClick={() => handleAddToQueue(video)}
                  disabled={loading}
                >
                  큐에 추가
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 큐 */}
      <div className="ytQueue">
        <div className="ytQueueHeader">
          <h3>재생 큐 ({queue.length})</h3>
          <div className="ytQueueActions">
            <button
              className="btn primary"
              onClick={handlePlayNext}
              disabled={loading || queue.length === 0}
            >
              다음 재생
            </button>
            <button
              className="btn"
              onClick={handleClearQueue}
              disabled={loading || queue.length === 0}
            >
              큐 비우기
            </button>
          </div>
        </div>
        {queue.length === 0 ? (
          <div className="empty">큐가 비어 있습니다.</div>
        ) : (
          <div className="ytList">
            {queue.map((item, idx) => (
              <div key={`${item.video_id}-${idx}`} className="ytQueueItem">
                <div className="ytQueueNum">{idx + 1}</div>
                <div className="ytQueueBody">
                  <div className="ytQueueTitle">{item.title}</div>
                  <div className="ytQueueChannel">{item.channel}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
