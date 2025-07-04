from flask import Flask, request, jsonify
from scraper import scrape_tiktok_sound
from apify_fetcher import fetch_top_videos_from_apify
import asyncio
import concurrent.futures
import os
from datetime import datetime

app = Flask(__name__)

# 🔧 ThreadPoolExecutor to run async calls in background threads
executor = concurrent.futures.ThreadPoolExecutor()

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        start_time = datetime.utcnow()
        print("📩 Request received at:", start_time)

        data = request.get_json()
        sound_url_or_id = data.get("sound_url")

        if not sound_url_or_id:
            print("❌ No sound_url provided.")
            return jsonify({"error": "Missing 'sound_url' in request"}), 400

        print("🔍 Step 1: Scraping Playwright...")
        scraped_data = scrape_tiktok_sound(sound_url_or_id)
        print("✅ Step 1 complete at:", datetime.utcnow())

        if scraped_data is None:
            return jsonify({"error": "Failed to scrape TikTok sound"}), 500

        print("🚀 Step 2: Running Apify fetch...")
        future = executor.submit(asyncio.run, fetch_top_videos_from_apify(sound_url_or_id))
        top_videos = future.result(timeout=50)
        print("✅ Step 2 complete at:", datetime.utcnow())

        if top_videos is None:
            return jsonify({"error": "Failed to fetch top videos"}), 500

        response = {
            "sound_title": scraped_data["title"],
            "ugc_count": scraped_data["ugc_count"],
            "top_videos": top_videos
        }

        print("📤 Responding at:", datetime.utcnow())
        return jsonify(response), 200

    except Exception as e:
        print("❌ Exception caught in /scrape route:", str(e))
        return jsonify({"error": str(e)}), 500


# 👇 Required for Fly.io
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
