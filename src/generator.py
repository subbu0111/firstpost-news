import json
import os
from datetime import datetime
from typing import List, Dict

class SiteGenerator:
    def __init__(self, data_file: str, output_file: str):
        self.data_file = data_file
        self.output_file = output_file
    
    def load_videos(self) -> List[Dict]:
        """Load videos from JSON database."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def generate_html(self):
        """Generate static HTML page for GitHub Pages."""
        videos = self.load_videos()
        
        # Sort by date (newest first)
        videos.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # Ensure docs directory exists (CRITICAL FIX)
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firstpost News Monitor</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ 
            text-align: center; 
            padding: 40px 20px; 
            color: white;
            margin-bottom: 30px;
        }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .subtitle {{ opacity: 0.9; font-size: 1.1em; }}
        .stats {{ 
            background: rgba(255,255,255,0.2); 
            padding: 15px; 
            border-radius: 10px; 
            display: inline-block;
            margin-top: 20px;
            backdrop-filter: blur(10px);
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
            gap: 25px; 
        }}
        .card {{ 
            background: white; 
            border-radius: 12px; 
            overflow: hidden; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.3); }}
        .thumbnail {{ width: 100%; height: 200px; object-fit: cover; }}
        .content {{ padding: 20px; }}
        .category {{ 
            display: inline-block; 
            background: #667eea; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 0.75em; 
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .category-live {{ background: #ff4757; }}
        h2 {{ font-size: 1.2em; margin-bottom: 12px; color: #222; line-height: 1.3; }}
        .summary {{ color: #555; font-size: 0.95em; margin-bottom: 15px; }}
        .highlights {{ 
            background: #f8f9fa; 
            padding: 12px; 
            border-radius: 8px; 
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }}
        .highlights ul {{ margin-left: 20px; color: #666; font-size: 0.9em; }}
        .highlights li {{ margin-bottom: 5px; }}
        .meta {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            font-size: 0.85em; 
            color: #888;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }}
        .watch-btn {{ 
            background: #ff0000; 
            color: white; 
            padding: 8px 16px; 
            border-radius: 6px; 
            text-decoration: none;
            font-weight: bold;
            transition: background 0.3s;
        }}
        .watch-btn:hover {{ background: #cc0000; }}
        footer {{ 
            text-align: center; 
            padding: 40px; 
            color: white; 
            opacity: 0.8;
            margin-top: 50px;
        }}
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            h1 {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📺 Firstpost Monitor</h1>
            <p class="subtitle">AI-summarized news updates from Firstpost YouTube Channel</p>
            <div class="stats">
                📊 Total Videos Archived: <strong>{len(videos)}</strong> | 
                Last Updated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</strong>
            </div>
        </header>
        
        <div class="grid">
"""
        
        for video in videos[:50]:  # Show last 50 videos max
            summary = video.get('summary', 'No summary available')
            category = video.get('category', 'News')
            is_live = category == 'LIVE'
            category_class = 'category category-live' if is_live else 'category'
            
            # Extract key points for display
            key_points_html = ""
            if 'key_points' in video and video['key_points']:
                points = video['key_points'][:3]
                key_points_html = "<ul>" + "".join([f"<li>{point}</li>" for point in points]) + "</ul>"
            
            html_content += f"""
            <article class="card">
                <img src="{video.get('thumbnail', '')}" alt="{video.get('title', '')}" class="thumbnail" loading="lazy">
                <div class="content">
                    <span class="{category_class}">{category}</span>
                    <h2>{video.get('title', 'Untitled')}</h2>
                    <div class="summary">{summary[:200]}...</div>
                    <div class="highlights">
                        <strong>🔑 Key Highlights:</strong>
                        {key_points_html}
                    </div>
                    <div class="meta">
                        <span>🕐 {video.get('published', 'Unknown date')[:10]}</span>
                        <a href="{video.get('link', '#')}" class="watch-btn" target="_blank">▶ Watch</a>
                    </div>
                </div>
            </article>
"""
        
        html_content += """
        </div>
        
        <footer>
            <p>Powered by AI | Auto-updated every 20 minutes | Built with ❤️ using GitHub Actions</p>
        </footer>
    </div>
</body>
</html>
"""
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated site with {len(videos)} videos")