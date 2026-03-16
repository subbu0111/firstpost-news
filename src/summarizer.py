from google import genai
from google.genai import types

class GeminiSummarizer:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-1.5-flash"
    
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
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Summarization error: {e}")
            return f"Error generating summary: {str(e)}"