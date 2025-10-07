# -*- coding: utf-8 -*-
import streamlit as st
import openai
import time
import os
from dotenv import load_dotenv
from config import TONE_OPTIONS, CONTENT_TYPES, MIN_WORDS, MAX_WORDS, DEFAULT_WORDS, APP_TITLE, APP_DESCRIPTION

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Content Writer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Apply global styles
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    .stApp > header {
        background: transparent;
    }
    
    .stApp > div[data-testid="stDecoration"] {
        background: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = ""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

# Generate content using OpenAI
def generate_content(topic, tone, content_type, word_count, api_key):
    try:
        openai.api_key = api_key
        
        prompt = f"Write a {content_type.lower()} about '{topic}'. Tone: {TONE_OPTIONS[tone]}. Target length: approximately {word_count} words. Make it engaging and well-structured with relevant headings where appropriate."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional content writer who creates high-quality, engaging content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=min(word_count * 2, 4000),
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating content: {str(e)}"

# Main app
def main():
    load_css()
    init_session_state()
    
    # Header
    st.markdown(f"""
        <div class="content-card">
            <h1 style="text-align: center; color: #2d3748; margin-bottom: 0.5rem; font-size: 2.5rem;">
                {APP_TITLE}
            </h1>
            <p style="text-align: center; color: #718096; margin-bottom: 2rem; font-size: 1.1rem;">
                {APP_DESCRIPTION}
            </p>
    """, unsafe_allow_html=True)
    
    # API Key input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Try to get API key from environment first
        env_api_key = os.getenv('OPENAI_API_KEY', '')
        api_key = st.text_input(
            "🔑 OpenAI API Key",
            value=env_api_key,
            type="password",
            placeholder="Enter your OpenAI API key",
            help="Your API key is not stored and only used for this session"
        )
        st.session_state.api_key = api_key
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to continue")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Input form
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        topic = st.text_input(
            "💡 Topic/Idea",
            placeholder="e.g., Benefits of remote work, AI in healthcare...",
            help="Enter the main topic or idea for your content"
        )
        
        content_type = st.selectbox(
            "📝 Content Type",
            CONTENT_TYPES,
            help="Choose the type of content you want to generate"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        tone = st.selectbox(
            "🎭 Tone",
            list(TONE_OPTIONS.keys()),
            help="Select the tone that best fits your audience"
        )
        
        word_count = st.slider(
            "📏 Word Count",
            min_value=MIN_WORDS,
            max_value=MAX_WORDS,
            value=DEFAULT_WORDS,
            step=50,
            help="Choose your desired content length"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Generate Content", use_container_width=True):
            if not topic.strip():
                st.error("❌ Please enter a topic or idea")
            else:
                with st.spinner("✨ Generating your content..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    content = generate_content(topic, tone, content_type, word_count, api_key)
                    st.session_state.generated_content = content
                    progress_bar.empty()
    
    # Display generated content
    if st.session_state.generated_content:
        st.markdown("""
        <div class="result-container">
            <h3 style="color: #2d3748; margin-bottom: 1rem;">📄 Generated Content</h3>
        """, unsafe_allow_html=True)
        
        # Content display
        st.markdown(st.session_state.generated_content)
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(st.session_state.generated_content, language=None)
                st.success("✅ Content ready to copy!")
        
        with col2:
            st.download_button(
                label="💾 Download as Text",
                data=st.session_state.generated_content,
                file_name=f"{topic.replace(' ', '_')}_content.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔄 Generate New", use_container_width=True):
                st.session_state.generated_content = ""
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e2e8f0;">
            <p style="color: #718096; font-size: 0.9rem;">
                Built with ❤️ using Streamlit & OpenAI GPT-4
            </p>
        </div>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()