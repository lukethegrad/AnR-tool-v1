import os
import httpx
import re

async def fetch_top_videos_from_apify(sound_url):
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("❌ ERROR: APIFY_TOKEN not set")
        return [{"error": "APIFY_TOKEN not set"}]

    # 🔍 Extract the sound ID
    match = re.search(r'/music/[^/]+-(\d+)', sound_url)
    if not match:
        print("❌ ERROR: Could not extract sound ID from URL")
        return [{"error": "Could not extract sound ID from URL"}]
    sound_id = match.group(1)

    print("🎯 DEBUG: Apify fetcher is running with sound_id =", sound_id)

    run_url = "https://api.apify.com/v2/acts/clockworks~tiktok-sound-scraper/runs?waitForFinish=1"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "musics": [sound_id],
        "resultsPerPage": 5,
        "shouldDownloadCovers": False,
        "shouldDownloadVideos": False
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            # Start actor run
            run_resp = await client.post(run_url, json=payload, headers=headers)
            run_resp.raise_for_status()
            run_data = run_resp.json()

            dataset_id = run_data.get("defaultDatasetId")
            if not dataset_id:
                print("❌ ERROR: No dataset ID returned from Apify run")
                return [{"error": "No dataset returned"}]

            dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true"
            dataset_resp = await client.get(dataset_url, headers=headers)
            dataset_resp.raise_for_status()

            items = dataset_resp.json()
            if not items:
                print("⚠️ WARNING: Apify dataset returned empty")
                return [{"error": "Apify returned no data"}]

            top_videos = []
            for item in items[:5]:
                top_videos.append({
                    "username": item.get("authorMeta", {}).get("name", "unknown"),
                    "views": item.get("stats", {}).get("playCount", "N/A"),
                    "posted": item.get("createTimeISO", "N/A")
                })

            return top_videos

    except Exception as e:
        print(f"❌ EXCEPTION in Apify fetcher: {e}")
        return [{"error": str(e)}]
