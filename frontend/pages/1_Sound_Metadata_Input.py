import streamlit as st

# Set page title and layout
st.set_page_config(page_title="TikTok Sound Input", layout="centered")

# Page header
st.title("🎵 TikTok Sound Metadata Tool")
st.markdown("Paste a TikTok sound URL or sound ID below. This will be used to pull metadata in later stages.")

# Input field
with st.form("sound_input_form"):
    sound_input = st.text_input("TikTok Sound URL or ID", placeholder="e.g. https://www.tiktok.com/music/1234567890")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if sound_input:
            st.session_state["sound_input"] = sound_input
            st.success("Sound input stored successfully.")
        else:
            st.warning("Please enter a valid TikTok sound URL or ID.")

# Display stored input
if "sound_input" in st.session_state:
    st.markdown("### Stored Sound Input")
    st.code(st.session_state["sound_input"], language="text")

# Placeholder for future data
st.markdown("---")
st.markdown("### 📊 Metadata Results (Coming Soon)")
st.info("Once the scraper is connected, metadata will appear here.")
