├── .github/
│   └── workflows/
│       └── monitor.yml          # Cron scheduler (every 10 mins)
├── data/
│   └── videos.json              # Database of processed videos (auto-updated)
├── docs/
│   └── index.html               # GitHub Pages site (auto-generated)
├── src/
│   ├── __init__.py
│   ├── config.py                # Environment & constants
│   ├── fetcher.py               # RSS + Transcript logic
│   ├── summarizer.py            # Gemini LLM integration
│   ├── notifier.py              # Telegram dispatcher
│   └── generator.py             # HTML site builder
├── .env.example
├── requirements.txt
└── README.md