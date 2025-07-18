# streamlit_gadget_app/app.py

import streamlit as st
import os
import base64

# Because 'predictor.py' is now inside our app folder, the import is simple and direct.
from engine.predictor import GadgetSearch

# --- Page Configuration ---
st.set_page_config(
    page_title="G.A.S.E.",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Asset Loading ---

@st.cache_data
def load_css(file_path):
    """Loads a CSS file and returns its content."""
    with open(file_path) as f:
        return f.read()

def get_audio_base64(file_path):
    """Encodes an audio file to base64 to embed it in HTML."""
    with open(file_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode()

def play_notification_sound():
    """Injects HTML to autoplay a notification sound."""
    try:
        audio_base64 = get_audio_base64("assets/notification.mp3")
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.components.v1.html(audio_html, height=0)
    except FileNotFoundError:
        st.warning("Notification sound file not found. Place `notification.mp3` in the `assets` folder.")
    except Exception as e:
        st.error(f"Could not play audio: {e}")


# --- Model Loading ---

@st.cache_resource
def load_search_engine():
    """
    Loads the GadgetSearch engine. The path is now relative to this script.
    Cached to run only once.
    """
    try:
        # The GadgetSearch class looks for a 'models/' folder by default,
        # so this works perfectly now.
        return GadgetSearch(model_path_prefix="models/")
    except Exception as e:
        st.error(f"Fatal Error: Could not load the search engine. Please ensure the `models` folder exists in the app directory and contains the required files. Details: {e}")
        return None

# --- Main Application UI ---

# Apply the custom CSS
st.markdown(f'<style>{load_css("style/style.css")}</style>', unsafe_allow_html=True)

st.title("G.A.S.E")
st.markdown("<p style='text-align: center; color: #8b949e;'>Gadget Assisted Search Engine</p>", unsafe_allow_html=True)

# Load the search engine
search_engine = load_search_engine()

if search_engine:
    # Use a form to prevent the app from re-running on every keystroke
    with st.form(key='search_form'):
        user_query = st.text_input(
            "Describe the function of the gadget you're looking for...",
            placeholder="e.g., I want to fly in the sky",
            label_visibility="collapsed"
        )
        submit_button = st.form_submit_button(label='🚀 Search')

    if submit_button and user_query:
        with st.spinner('Searching the gadget-verse...'):
            results = search_engine.search(user_query, k=3)

        st.markdown("---")

        if results:
            # Play the sound effect if results are found
            play_notification_sound()
            st.subheader("Top Results Found:")
            for res in results:
                card_html = f"""
                <div class="result-card">
                    <div class="gadget-name">{res['gadget_name']}</div>
                    <div class="similarity-score">Similarity: {res['similarity']:.2f}</div>
                    <p class="gadget-function">{res['function']}</p>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.warning("No gadgets found matching your description. Try phrasing it differently.")

    st.markdown("<br><br><p style='text-align: center; color: #30363d;'>Enter a function to begin.</p>", unsafe_allow_html=True)