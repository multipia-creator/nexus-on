import json
import re
import time
from typing import Any, Dict, List, Optional

import requests
import redis


_ISO8601_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _duration_to_sec(iso: str) -> Optional[int]:
    m = _ISO8601_RE.fullmatch((iso or "").strip())
    if not m:
        return None
    h = int(m.group(1) or 0)
    mm = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mm * 60 + s


class YouTubeClient:
    """YouTube Data API v3 thin client with tenant-scoped TTL cache.

    Requires env/config:
      - api_key: YouTube Data API key
      - base_url: default https://www.googleapis.com/youtube/v3
    """

    def __init__(self, redis_url: str, api_key: str, base_url: str = "https://www.googleapis.com/youtube/v3"):
        self.api_key = (api_key or "").strip()
        self.base_url = base_url.rstrip("/")
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    def enabled(self) -> bool:
        return bool(self.api_key)

    def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self.r.get(key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def _cache_set(self, key: str, value: Dict[str, Any], ttl_sec: int) -> None:
        self.r.set(key, json.dumps(value, ensure_ascii=False))
        if ttl_sec > 0:
            self.r.expire(key, int(ttl_sec))

    def search(self,
               tenant: str,
               query: str,
               max_results: int = 8,
               region: str = "KR",
               language: str = "ko",
               filters: Optional[Dict[str, Any]] = None,
               cache_ttl_sec: int = 3600) -> List[Dict[str, Any]]:
        query = (query or "").strip()
        if not query:
            return []
        filters = filters or {}
        kind = (filters.get("type") or "video").lower()
        safe_search = (filters.get("safe_search") or "moderate").lower()
        duration = (filters.get("duration") or "any").lower()

        cache_key = f"nexus:yt:{tenant}:search:{region}:{language}:{kind}:{safe_search}:{duration}:{max_results}:{query}"
        cached = self._cache_get(cache_key)
        if cached and isinstance(cached.get("items"), list):
            return cached["items"]

        if not self.enabled():
            return []

        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": query,
            "maxResults": max(1, min(int(max_results), 12)),
            "type": "video" if kind in {"video", "any"} else kind,
            "regionCode": region,
            "relevanceLanguage": language,
            "safeSearch": safe_search,
        }
        url = f"{self.base_url}/search"
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        video_ids: List[str] = []
        base_items: List[Dict[str, Any]] = []
        for it in (data.get("items") or []):
            vid = ((it.get("id") or {}).get("videoId") or "").strip()
            if not vid:
                continue
            sn = it.get("snippet") or {}
            base_items.append({
                "video_id": vid,
                "title": sn.get("title") or "",
                "channel_title": sn.get("channelTitle") or "",
                "published_at": sn.get("publishedAt") or "",
                "thumbnail": ((sn.get("thumbnails") or {}).get("high") or {}).get("url")
                or ((sn.get("thumbnails") or {}).get("default") or {}).get("url")
                or "",
            })
            video_ids.append(vid)

        details = self._videos_list(video_ids)
        detail_map = {d["video_id"]: d for d in details}
        out: List[Dict[str, Any]] = []
        for bi in base_items:
            d = detail_map.get(bi["video_id"], {})
            out.append({
                **bi,
                "duration_sec": d.get("duration_sec"),
                "view_count": d.get("view_count"),
                "link": f"https://www.youtube.com/watch?v={bi['video_id']}",
                "fetched_at": _utc_iso(),
            })

        self._cache_set(cache_key, {"items": out, "ts": _utc_iso()}, int(cache_ttl_sec))
        return out

    def _videos_list(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        if (not self.enabled()) or (not video_ids):
            return []
        ids = ",".join(video_ids[:50])
        url = f"{self.base_url}/videos"
        params = {
            "key": self.api_key,
            "part": "contentDetails,statistics",
            "id": ids,
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        out: List[Dict[str, Any]] = []
        for it in (data.get("items") or []):
            vid = (it.get("id") or "").strip()
            cd = it.get("contentDetails") or {}
            st = it.get("statistics") or {}
            out.append({
                "video_id": vid,
                "duration_sec": _duration_to_sec(cd.get("duration") or ""),
                "view_count": int(st.get("viewCount") or 0),
            })
        return out
