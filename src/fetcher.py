import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class YouTubeFetcher:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        # Create API instance for newer versions
        try:
            self.ytt_api = YouTubeTranscriptApi()
        except:
            self.ytt_api = None
    
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
        """Universal transcript fetcher - works with all API versions"""
        try:
            # Try newer API first (v1.0+)
            if self.ytt_api:
                try:
                    transcript_list = self.ytt_api.fetch(video_id)
                    if hasattr(transcript_list, '__iter__'):
                        full_text = ' '.join([item.text if hasattr(item, 'text') else item['text'] for item in transcript_list])
                    else:
                        full_text = str(transcript_list)
                    print(f"   ✅ Got transcript: {len(full_text)} chars")
                    return full_text
                except AttributeError:
                    pass  # Fall through to old method
            
            # Try older API (v0.6.x)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            if transcript_list:
                full_text = ' '.join([item['text'] for item in transcript_list])
                print(f"   ✅ Got transcript: {len(full_text)} chars")
                return full_text
                
        except TranscriptsDisabled:
            print(f"   ⚠️ Transcripts disabled")
        except NoTranscriptFound:
            print(f"   ⚠️ No transcript found")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
        
        return None