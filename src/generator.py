import os
import json
from datetime import datetime
from dateutil import parser
import pytz

class WebsiteGenerator:
    def __init__(self, data_file='data/videos.json', output_file='docs/index.html'):
        self.data_file = data_file
        self.output_file = output_file
        self._ensure_dir(self.data_file)
        self.ist_tz = pytz.timezone('Asia/Kolkata')
    
    def _ensure_dir(self, filepath):
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def _to_ist(self, date_string):
        """Convert UTC to IST"""
        try:
            dt = parser.parse(date_string)
            dt_ist = dt.astimezone(self.ist_tz)
            return dt_ist.strftime('%Y-%m-%d %H:%M IST')
        except:
            return date_string
    
    def video_exists(self, video_id):
        if not os.path.exists(self.data_file):
            return False
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
            return any(v['id'] == video_id for v in videos)
        except:
            return False
    
    def save_video(self, video_data):
        self._ensure_dir(self.data_file)
        videos = []
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    videos = json.load(f)
            except:
                videos = []
        
        existing = next((i for i, v in enumerate(videos) if v['id'] == video_data['id']), None)
        if existing is not None:
            videos[existing] = video_data
        else:
            videos.append(video_data)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
    
    def load_videos(self):
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def generate_html(self):
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        videos = self.load_videos()
        videos.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        now_ist = datetime.now(self.ist_tz).strftime('%Y-%m-%d %H:%M:%S IST')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firstpost News Monitor</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ background: white; border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        h1 {{ color: #333; margin-bottom: 5px; }}
        .subtitle {{ color: #666; margin-bottom: 30px; font-size: 0.9em; }}
        .video-card {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
        .video-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 8px; }}
        .video-title a {{ color: #2c3e50; text-decoration: none; }}
        .video-title a:hover {{ color: #667eea; }}
        .meta {{ color: #666; font-size: 0.85em; margin-bottom: 10px; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold; margin-left: 8px; }}
        .badge-live {{ background: #e74c3c; color: white; }}
        .badge-summary {{ background: #27ae60; color: white; }}
        .badge-no-transcript {{ background: #f39c12; color: white; }}
        .summary {{ line-height: 1.6; color: #444; margin-top: 10px; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 0.85em; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 Firstpost YouTube Monitor</h1>
        <p class="subtitle">Last updated: {now_ist} | Runs every 20 minutes</p>
'''
        
        if not videos:
            html += '<div class="video-card"><p>No videos processed yet.</p></div>'
        else:
            for v in videos:
                title = v.get('title', 'Unknown')
                status = v.get('status', 'unknown')
                summary = v.get('summary', '')
                url = v.get('url', '#')
                published = self._to_ist(v.get('published', ''))
                
                if status == 'live':
                    badge = '<span class="badge badge-live">🔴 LIVE</span>'
                    content = '<p>Live stream active when detected</p>'
                elif status == 'no_transcript':
                    badge = '<span class="badge badge-no-transcript">📝 No Transcript</span>'
                    content = f'<p><a href="{url}" target="_blank">Watch on YouTube</a> — Transcript not available</p>'
                else:
                    badge = '<span class="badge badge-summary">🤖 AI Summary</span>'
                    formatted = summary.replace('\n', '<br>')
                    content = f'<div class="summary">{formatted}</div>'
                
                html += f'''
        <div class="video-card">
            <div class="video-title"><a href="{url}" target="_blank">{title}</a>{badge}</div>
            <div class="meta">Published: {published}</div>
            {content}
        </div>'''
        
        html += '''
        <div class="footer">
            <p>Generated automatically by GitHub Actions | Powered by Gemini AI</p>
        </div>
    </div>
</body>
</html>'''
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   ✅ Generated website: {self.output_file} ({len(videos)} videos)")

if __name__ == "__main__":
    gen = WebsiteGenerator()
    gen.generate_html()