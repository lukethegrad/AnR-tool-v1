from flask import Flask, request, jsonify
from scraper import scrape_tiktok_sound
from apify_fetcher import fetch_top_videos

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

        # Get top 5 videos from Apify
        top_videos = fetch_top_videos(sound_url_or_id)
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
