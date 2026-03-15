import google.generativeai as genai
from typing import Optional

class GeminiSummarizer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def summarize(self, transcript: str, title: str) -> Optional[str]:
        """Generate summary and highlights from transcript."""
        if not transcript or len(transcript) < 100:
            return None
        
        # Truncate if too long (Gemini Flash has 1M context, but being safe)
        truncated = transcript[:15000] if len(transcript) > 15000 else transcript
        
        prompt = f"""Analyze this Firstpost news video transcript and provide:

**Context**: Video titled "{title}"

**Instructions**:
1. Provide a concise 2-sentence summary of the key news
2. Extract 3-4 key bullet points highlighting main facts, quotes, or implications
3. Identify the primary category (Politics, World, Business, Defense, or General)
4. Keep bullet points under 100 characters each

**Format**:
SUMMARY: [Your 2-sentence summary]
CATEGORY: [Category]
KEY_POINTS:
• [Point 1]
• [Point 2]
• [Point 3]

**Transcript**:
{truncated}"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return None
    
    def format_for_telegram(self, structured_summary: str, video_title: str, link: str) -> str:
        """Convert structured summary to Telegram HTML format."""
        lines = structured_summary.split('\n')
        category = "General"
        summary_text = ""
        key_points = []
        
        for line in lines:
            if line.startswith('CATEGORY:'):
                category = line.replace('CATEGORY:', '').strip()
            elif line.startswith('SUMMARY:'):
                summary_text = line.replace('SUMMARY:', '').strip()
            elif line.startswith('•'):
                key_points.append(line.strip())
        
        points_text = '\n'.join([f"• {point.replace('•', '').strip()}" for point in key_points[:4]])
        
        message = f"""🚨 <b>Firstpost {category}</b>

<b>{video_title}</b>

📰 <b>Summary:</b>
{summary_text}

🔑 <b>Highlights:</b>
{points_text}

<a href="{link}">📺 Watch Video</a>"""
        
        return message