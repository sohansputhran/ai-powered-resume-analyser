import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import json

# Import custom modules
from services.gemini_service import GeminiService
from services.langchain_service import LangChainService
from services.resume_processor import ResumeProcessor
from utils.file_handler import FileHandler
from config.settings import APP_CONFIG

# Page configuration
st.set_page_config(
    page_title="AI-Powered Resume Analyser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.keyword-match {
    background-color: #d4edda;
    color: #155724;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    margin: 0.1rem;
    display: inline-block;
}
.keyword-missing {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    margin: 0.1rem;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

def initialize_services():
    """Initialize all required services"""
    if 'services_initialized' not in st.session_state:
        st.session_state.gemini_service = GeminiService()
        st.session_state.langchain_service = LangChainService()
        st.session_state.resume_processor = ResumeProcessor()
        st.session_state.file_handler = FileHandler()
        st.session_state.services_initialized = True

def display_header():
    """Display the main header"""
    st.markdown('<h1 class="main-header">📄 AI-Powered Resume Analyser</h1>', unsafe_allow_html=True)
    st.markdown("---")

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

def process_documents(resume_file, job_file, job_text):
    """Process uploaded documents and extract text"""
    resume_text = ""
    job_description_text = ""
    
    # Extract resume text
    if resume_file:
        resume_text = st.session_state.file_handler.extract_text_from_file(resume_file)
        
    # Extract job description text
    if job_file:
        job_description_text = st.session_state.file_handler.extract_text_from_file(job_file)
    elif job_text.strip():
        job_description_text = job_text
        
    return resume_text, job_description_text

def analyze_documents(resume_text: str, job_description_text: str) -> Dict:
    """Analyze resume and job description using AI"""
    with st.spinner("🤖 Analyzing documents with AI..."):
        try:
            # Extract job requirements
            job_analysis = st.session_state.langchain_service.analyze_job_description(job_description_text)
            
            # Analyze resume
            resume_analysis = st.session_state.langchain_service.analyze_resume(resume_text, job_analysis)
            
            # Generate tailored resume
            tailored_resume = st.session_state.langchain_service.generate_tailored_resume(
                resume_text, job_analysis, resume_analysis
            )
            
            return {
                'job_analysis': job_analysis,
                'resume_analysis': resume_analysis,
                'tailored_resume': tailored_resume
            }
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            return None

def display_analysis_results(analysis_results: Dict):
    """Display analysis results with visualizations"""
    if not analysis_results:
        return
        
    job_analysis = analysis_results['job_analysis']
    resume_analysis = analysis_results['resume_analysis']
    
    st.header("📊 Analysis Results")
    
    # Metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        match_score = resume_analysis.get('match_score', 0)
        st.metric("Match Score", f"{match_score}%", 
                 delta=f"{match_score - 70}%" if match_score >= 70 else f"{match_score - 70}%")
    
    with col2:
        matched_keywords = len(resume_analysis.get('matched_keywords', []))
        st.metric("Matched Keywords", matched_keywords)
    
    with col3:
        missing_keywords = len(resume_analysis.get('missing_keywords', []))
        st.metric("Missing Keywords", missing_keywords)
    
    with col4:
        total_requirements = len(job_analysis.get('key_skills', []))
        st.metric("Total Requirements", total_requirements)
    
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Job Requirements", "🔍 Resume Analysis", "📈 Keyword Analysis", "✨ Tailored Resume"])
    
    with tab1:
        display_job_analysis(job_analysis)
    
    with tab2:
        display_resume_analysis(resume_analysis)
    
    with tab3:
        display_keyword_analysis(resume_analysis)
    
    with tab4:
        display_tailored_resume(analysis_results['tailored_resume'])

def display_job_analysis(job_analysis: Dict):
    """Display job description analysis"""
    st.subheader("Key Requirements Extracted")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Technical Skills:**")
        for skill in job_analysis.get('technical_skills', []):
            st.write(f"• {skill}")
            
        st.write("**Experience Level:**")
        st.write(job_analysis.get('experience_level', 'Not specified'))
    
    with col2:
        st.write("**Soft Skills:**")
        for skill in job_analysis.get('soft_skills', []):
            st.write(f"• {skill}")
            
        st.write("**Education Requirements:**")
        st.write(job_analysis.get('education', 'Not specified'))

def display_resume_analysis(resume_analysis: Dict):
    """Display resume analysis results"""
    st.subheader("Resume Strengths & Gaps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Strengths:**")
        for strength in resume_analysis.get('strengths', []):
            st.write(f"✅ {strength}")
    
    with col2:
        st.write("**Areas for Improvement:**")
        for gap in resume_analysis.get('gaps', []):
            st.write(f"⚠️ {gap}")

def display_keyword_analysis(resume_analysis: Dict):
    """Display keyword matching analysis with visualizations"""
    matched_keywords = resume_analysis.get('matched_keywords', [])
    missing_keywords = resume_analysis.get('missing_keywords', [])
    
    # Keyword match visualization
    if matched_keywords or missing_keywords:
        fig = go.Figure(data=[
            go.Bar(name='Matched', x=['Keywords'], y=[len(matched_keywords)], marker_color='green'),
            go.Bar(name='Missing', x=['Keywords'], y=[len(missing_keywords)], marker_color='red')
        ])
        fig.update_layout(barmode='group', title='Keyword Match Analysis')
        st.plotly_chart(fig, use_container_width=True)
    
    # Display keyword lists
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Keywords")
        for keyword in matched_keywords:
            st.markdown(f'<span class="keyword-match">{keyword}</span>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("❌ Missing Keywords")
        for keyword in missing_keywords:
            st.markdown(f'<span class="keyword-missing">{keyword}</span>', unsafe_allow_html=True)

def display_tailored_resume(tailored_resume: str):
    """Display the tailored resume with download options"""
    st.subheader("Your Tailored Resume")
    
    # Display tailored resume
    st.text_area("Tailored Resume Content", tailored_resume, height=400, key="tailored_content")
    
    # Download and copy options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Download as TXT",
            data=tailored_resume,
            file_name="tailored_resume.txt",
            mime="text/plain"
        )
    
    with col2:
        if st.button("📋 Copy to Clipboard"):
            # Note: This requires pyperclip but may not work in all environments
            try:
                import pyperclip
                pyperclip.copy(tailored_resume)
                st.success("Copied to clipboard!")
            except:
                st.info("Copy to clipboard not available. Please select and copy manually.")
    
    with col3:
        # Convert to downloadable formats could be added here
        pass

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

def main():
    """Main application function"""
    # Initialize services
    initialize_services()
    
    # Display header
    display_header()
    
    # Display sidebar
    settings = display_sidebar()
    
    # File upload section
    resume_file, job_file, job_text = display_file_upload_section()
    
    # Process documents when uploaded
    if (resume_file and (job_file or job_text.strip())):
        resume_text, job_description_text = process_documents(resume_file, job_file, job_text)
        
        if resume_text and job_description_text:
            st.success("Documents processed successfully!")
            
            # Analyze button
            if st.button("🚀 Analyze & Generate Tailored Resume", type="primary"):
                analysis_results = analyze_documents(resume_text, job_description_text)
                
                if analysis_results:
                    # Store results in session state
                    st.session_state.analysis_results = analysis_results
                    
    # Display results if available
    if 'analysis_results' in st.session_state:
        display_analysis_results(st.session_state.analysis_results)

if __name__ == "__main__":
    main()