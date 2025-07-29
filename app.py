from google import genai
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def display_header():
    """Display the main header"""
    st.markdown('<h1 class="main-header">📄 AI-Powered Resume Analyser</h1>', unsafe_allow_html=True)
    st.markdown("---")

def display_sidebar():
    """Display sidebar with additional options"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model settings
        st.subheader("AI Model Settings")
        creativity = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
        
        # Analysis options
        st.subheader("Analysis Options")
        include_soft_skills = st.checkbox("Include Soft Skills Analysis", True)
        detailed_feedback = st.checkbox("Detailed Feedback", True)
        
        # Tips section
        st.header("💡 Tips")
        st.markdown("""
        **For best results:**
        - Upload a well-formatted resume
        - Provide a detailed job description
        - Review suggestions carefully
        - Customize the output to your style
        """)
        
        return {
            'creativity': creativity,
            'include_soft_skills': include_soft_skills,
            'detailed_feedback': detailed_feedback
        }

def display_file_upload_section():
    """Display file upload section"""
    st.header("📁 Upload Documents")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resume")
        resume_file = st.file_uploader(
            "Upload your resume",
            type=['pdf', 'docx', 'txt'],
            key="resume_upload"
        )
        
    with col2:
        st.subheader("Job Description")
        job_file = st.file_uploader(
            "Upload job description",
            type=['pdf', 'docx', 'txt'],
            key="job_upload"
        )
        
    # Alternative text input for job description
    st.subheader("Or paste job description text:")
    job_text = st.text_area("Job Description", height=200, key="job_text_input")
    
    return resume_file, job_file, job_text

def main():
    # Main application function
    display_header()
    display_sidebar()
    resume_file, job_file, job_text = display_file_upload_section()


if __name__ == "__main__":
    main()