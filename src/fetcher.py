import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

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
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            if transcript_list:
                full_text = ' '.join([item['text'] for item in transcript_list])
                print(f"   ✅ Got transcript: {len(full_text)} chars")
                return full_text
            return None
        except TranscriptsDisabled:
            print(f"   ⚠️ Transcripts disabled")
            return None
        except NoTranscriptFound:
            print(f"   ⚠️ No transcript found")
            return None
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            return None