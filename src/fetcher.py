import feedparser
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeFetcher:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        self.ytt = YouTubeTranscriptApi()  # Create instance for v1.0+
    
    def get_latest_videos(self, max_results=10):
        feed = feedparser.parse(self.rss_url)
        videos = []
        for entry in feed.entries[:max_results]:
            video_id = entry.yt_videoid
            is_live = 'live' in str(getattr(entry, 'media_status', '')).lower()
            videos.append({
                'id': video_id,
                'title': entry.title,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'published': entry.published,
                'is_live': is_live
            })
        return videos
    
    def get_transcript(self, video_id):
        try:
            # v1.0+ syntax: use .fetch() on instance
            transcript = self.ytt.fetch(video_id)
            full_text = ' '.join([snippet.text for snippet in transcript])
            print(f"   ✅ Transcript: {len(full_text)} chars")
            return full_text
        except Exception as e:
            print(f"   ⚠️ No transcript: {str(e)[:60]}")
            return None