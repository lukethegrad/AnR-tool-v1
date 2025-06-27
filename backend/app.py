from flask import Flask, request, jsonify
from scraper import scrape_tiktok_sound
from apify_fetcher import fetch_top_videos_from_apify
import asyncio

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        sound_url_or_id = data.get("sound_url")

        if not sound_url_or_id:
            return jsonify({"error": "Missing 'sound_url' in request"}), 400

        # Get title and UGC count from Playwright
        scraped_data = scrape_tiktok_sound(sound_url_or_id)
        if scraped_data is None:
            return jsonify({"error": "Failed to scrape TikTok sound"}), 500

        # Get top 5 videos from Apify (corrected async call)
        top_videos = asyncio.run(fetch_top_videos_from_apify(sound_url_or_id))
        if top_videos is None:
            return jsonify({"error": "Failed to fetch top videos"}), 500

        response = {
            "sound_title": scraped_data["title"],
            "ugc_count": scraped_data["ugc_count"],
            "top_videos": top_videos
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Required for Fly.io to detect the app and serve on port 8080
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
