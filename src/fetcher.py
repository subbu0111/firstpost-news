import feedparser
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeFetcher:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    
    def get_latest_videos(self, max_results=5):
        try:
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
        except Exception as e:
            print(f"❌ RSS Error: {e}")
            return []
    
    def get_transcript(self, video_id):
        """Universal method - tries multiple API versions"""
        try:
            # Method 1: Try the newer fetch() method (v1.0+)
            try:
                ytt = YouTubeTranscriptApi()
                transcript = ytt.fetch(video_id)
                # Handle new response format
                if transcript:
                    texts = []
                    for snippet in transcript:
                        if hasattr(snippet, 'text'):
                            texts.append(snippet.text)
                        elif isinstance(snippet, dict):
                            texts.append(snippet.get('text', ''))
                    full_text = ' '.join(texts)
                    if full_text:
                        print(f"   ✅ Transcript fetched (v1.0 API): {len(full_text)} chars")
                        return full_text
            except (AttributeError, TypeError):
                pass  # Fall through to old method
            
            # Method 2: Try old static method (v0.6.x)
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                if transcript_list:
                    full_text = ' '.join([item['text'] for item in transcript_list])
                    print(f"   ✅ Transcript fetched (v0.6 API): {len(full_text)} chars")
                    return full_text
            except AttributeError:
                pass
            
            print("   ⚠️ Could not fetch transcript with any method")
            return None
            
        except Exception as e:
            print(f"   ⚠️ Transcript unavailable: {str(e)[:80]}")
            return None