from flask import Flask, request, jsonify
from scraper import scrape_tiktok_sound
from apify_fetcher import fetch_top_videos_from_apify
import asyncio
import concurrent.futures
import os

app = Flask(__name__)

# 🔧 ThreadPoolExecutor to run async calls in background threads
executor = concurrent.futures.ThreadPoolExecutor()

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        sound_url_or_id = data.get("sound_url")

        if not sound_url_or_id:
            return jsonify({"error": "Missing 'sound_url' in request"}), 400

        # 1️⃣ Get title + UGC count from Playwright (sync)
        scraped_data = scrape_tiktok_sound(sound_url_or_id)
        if scraped_data is None:
            return jsonify({"error": "Failed to scrape TikTok sound"}), 500

        # 2️⃣ Run Apify call as async in background thread
        future = executor.submit(asyncio.run, fetch_top_videos_from_apify(sound_url_or_id))
        top_videos = future.result(timeout=50)  # Adjust timeout if needed

        if top_videos is None:
            return jsonify({"error": "Failed to fetch top videos"}), 500

        # 3️⃣ Combine & return
        response = {
            "sound_title": scraped_data["title"],
            "ugc_count": scraped_data["ugc_count"],
            "top_videos": top_videos
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 👇 Required for Fly.io
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
