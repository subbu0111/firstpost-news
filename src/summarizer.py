import google.generativeai as genai

class GeminiSummarizer:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def summarize(self, text, title):
        """Summarize video transcript using Gemini Flash"""
        prompt = f"""Analyze this YouTube video transcript from Firstpost news channel.

Video Title: {title}

Transcript:
{text[:15000]}

Provide a concise summary in 3-4 bullet points covering:
1. Main news story/topic
2. Key points or developments mentioned
3. Any important statements or decisions

Keep it factual and neutral. Use plain text without markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Summarization error: {e}")
            return f"Error generating summary: {str(e)}"