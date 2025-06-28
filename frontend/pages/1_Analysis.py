import streamlit as st
import requests
import pandas as pd

# Config
st.set_page_config(page_title="TikTok Sound Input", layout="centered")
BACKEND_URL = "https://anr-tool-v1.fly.dev/scrape"  # ✅ Your actual Fly.io backend URL

# Title
st.title("🎵 TikTok Sound Metadata Tool")
st.markdown("Paste a TikTok sound URL or sound ID below. This will be used to pull metadata in later stages.")

# Input
with st.form("sound_input_form"):
    sound_input = st.text_input("TikTok Sound URL or ID", placeholder="e.g. https://www.tiktok.com/music/1234567890")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not sound_input:
            st.warning("Please enter a valid TikTok sound URL or ID.")
        else:
            with st.spinner("Scraping TikTok data..."):
                try:
                    response = requests.post(
                        BACKEND_URL,
                        json={"sound_url": sound_input},
                        timeout=30
                    )

                    st.code(f"🔍 Raw response text:\n{response.text}")
                    st.write(f"Status code: {response.status_code}")

                    if response.status_code != 200:
                        try:
                            error_data = response.json()
                            st.error(f"❌ Backend error: {error_data.get('error', 'Unknown error')}")
                        except Exception:
                            st.error("❌ Backend returned non-JSON error.")
                    else:
                        data = response.json()
                        st.session_state["sound_input"] = sound_input
                        st.success("✅ Sound input stored successfully.")

                        # Display metadata
                        st.markdown("### ✅ Metadata Results")

                        st.subheader("Sound Title")
                        st.markdown(f"**{data['sound_title']}**")

                        st.subheader("Total UGC Count")
                        st.markdown(f"{data['ugc_count']:,} videos")

                        st.subheader("Top 5 Videos")
                        df = pd.DataFrame(data["top_videos"])
                        df.columns = ["Username", "Views", "Post Date"]
                        st.dataframe(df)

                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Request failed: {e}")
                except ValueError as json_error:
                    st.error(f"❌ JSON decode failed: {json_error}")

# Fallback display for stored input
if "sound_input" in st.session_state and not submitted:
    st.markdown("### Stored Sound Input")
    st.code(st.session_state["sound_input"], language="text")
