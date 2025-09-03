import streamlit as st
import sys
import os
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.services.few_shot import FewShotPosts
from src.services.post_service import generate_post

# --- Page Config ---
st.set_page_config(
    page_title="LinkedIn Post Generator 🚀",
    # page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom Styles ---
st.markdown(
    """
    <style>
    .block-container { max-width: 850px !important; }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #3b82f6);
        color: white;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #4f46e5, #2563eb);
    }
    .post-box {
        background-color: #f9fafb;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
        font-size: 15px;
        line-height: 1.6;
        color: #000000;   /* ✅ Forces text to black */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Options ---
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]

def main():
    # Header
    st.title("✍️ LinkedIn Post Creator Pro")
    st.caption("Generate professional, engaging LinkedIn posts in seconds 🚀")
    st.markdown("---")

    # Load Tags
    fs = FewShotPosts()
    try:
        tags = sorted(set(fs.get_tags()))
        if not tags:
            raise ValueError("No tags found")
    except Exception:
        tags = [
            "AI & Tech", "Startup", "Career", "Personal Story", "Industry Insights",
            "Leadership", "Productivity", "Marketing", "Job Search", "Self Improvement",
            "Future Of Work", "Work Culture", "Networking", "Time Management",
            "Personal Growth", "Scams"
        ]

    # --- Input Controls ---
    st.subheader("⚡ Customize Your Post")
    col1, col2 = st.columns(2)

    with col1:
        selected_tag = st.selectbox("Topic", options=tags)

    with col2:
        selected_length = st.radio("Length", options=length_options, horizontal=True)

    selected_language = st.radio("Language", options=language_options, horizontal=True)

    st.markdown("---")

    # --- Generate Button ---
    if st.button("✨ Generate Post", use_container_width=True):
        if not selected_tag:
            st.error("Please select a topic.")
            return

        with st.spinner("Crafting your LinkedIn magic..."):
            try:
                post_content = generate_post(selected_length, selected_language, selected_tag)

                st.subheader("📄 Your Generated Post")
                st.markdown(f"<div class='post-box'>{post_content}</div>", unsafe_allow_html=True)

                st.download_button(
                    "📥 Download Post",
                    post_content,
                    file_name="linkedin_post.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Error generating post: {e}")

    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit + Groq")

if __name__ == "__main__":
    main()
