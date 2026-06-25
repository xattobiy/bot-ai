#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
DIET ASSISTANT TELEGRAM BOT - RENDER WEB SERVICE VERSION
=============================================================================
This file runs the bot as a Render Web Service with health check endpoint.

For Render deployment:
1. Set Start Command: gunicorn app:app
2. Add environment variables: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, ADMIN_ID
=============================================================================
"""

import os
import threading
from flask import Flask

# Create Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for Render"""
    return {"status": "ok", "service": "Diet Assistant Bot"}, 200

@app.route('/health')
def health():
    """Alternative health check endpoint"""
    return {"status": "healthy"}, 200

# Import and run the bot in a background thread
def run_bot():
    """Run the Telegram bot"""
    # Import here to avoid circular imports
    import colab_diet_bot
    colab_diet_bot.run_bot()

# Start bot in background thread when app starts
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    # For local testing
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
