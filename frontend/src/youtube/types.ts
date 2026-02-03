export interface YouTubeVideo {
  video_id: string
  title: string
  channel_title: string
  thumbnail: string
  duration_sec: number | null
  view_count: number | null
  link: string
  published_at: string
  fetched_at: string
}

export interface YouTubeQueueItem {
  video_id: string
  title: string
  channel: string
  embed_url: string
  added_at?: string
}
