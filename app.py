import streamlit as st
import google.generativeai as genai
import requests
import re
import os
from moviepy import VideoFileClip, concatenate_videoclips


st.set_page_config(page_title="Movie Recap Automation", layout="wide")
st.title("🎬 All-in-One Movie Recap Automation Tool")

# Sidebar - API Keys setup
st.sidebar.header("🔑 API Configurations")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
elevenlabs_key = st.sidebar.text_input("ElevenLabs API Key", type="password")

# Tabs
tab1, tab2, tab3 = st.tabs(["1. Subtitle & Script", "2. Voiceover", "3. Video Processing"])

# Tab 1: Subtitle Cleaner & Gemini Script Generator
with tab1:
    st.header("📝 Subtitle Processing & Script Generation")
    srt_file = st.file_uploader("Upload Subtitle File (.srt)", type=["srt"])
    
    if srt_file and gemini_key:
        srt_text = srt_file.read().decode("utf-8")
        clean_text = re.sub(r'\d+\n\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d\n', '', srt_text)
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        
        st.subheader("Cleaned Subtitle Preview")
        st.text_area("Subtitle Content", clean_text[:1000], height=150)
        
        if st.button("Generate Myanmar Script"):
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"Translate and rewrite this subtitle into an engaging Burmese Movie Recap script. Make it exciting:\n\n{clean_text[:4000]}"
            
            with st.spinner("Generating Burmese Script..."):
                response = model.generate_content(prompt)
                st.session_state['script'] = response.text
                st.success("Script Generated Successfully!")
                st.text_area("Generated Script", st.session_state['script'], height=250)

# Tab 2: ElevenLabs Voiceover Generation
with tab2:
    st.header("🎙️ Voiceover Production")
    script_input = st.text_area("Script for Voiceover", value=st.session_state.get('script', ''), height=200)
    voice_id = st.text_input("ElevenLabs Voice ID", value="21m00Tcm4TlvDq8ikWAM")
    
    if st.button("Generate Audio"):
        if elevenlabs_key and script_input:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "json",
                "xi-api-key": elevenlabs_key
            }
            data = {
                "text": script_input,
                "model_id": "eleven_multilingual_v2"
            }
            with st.spinner("Generating Voiceover..."):
                res = requests.post(url, json=data, headers=headers)
                if res.status_code == 200:
                    with open("output.mp3", "wb") as f:
                        f.write(res.content)
                    st.audio("output.mp3")
                    st.success("Voiceover Ready!")
                else:
                    st.error(f"Error: {res.text}")

# Tab 3: Copyright-Safe Video Auto Edit
with tab3:
    st.header("✂️ Auto Video Editing (3s Play / 3s Freeze Frame)")
    video_file = st.file_uploader("Upload Raw Movie Clip (.mp4)", type=["mp4"])
    
    if video_file and st.button("Start Editing"):
        with open("input.mp4", "wb") as f:
            f.write(video_file.read())
            
        with st.spinner("Processing Video..."):
            clip = VideoFileClip("input.mp4")
            duration = int(clip.duration)
            clips = []
            
            for i in range(0, duration, 6):
                sub = clip.subclip(i, min(i+3, duration))
                clips.append(sub)
                if i+3 < duration:
                    freeze = clip.to_ImageClip(i+3).set_duration(3)
                    clips.append(freeze)
                    
            final = concatenate_videoclips(clips)
            final.write_videofile("final_output.mp4", codec="libx264")
            st.video("final_output.mp4")
            st.success("Editing Complete!")
