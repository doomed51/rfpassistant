"""
RFP Alignment Assistant - Streamlit Application

A web application that helps consulting teams quickly parse RFPs 
and generate internal alignment materials using AI.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

# Import utility modules
from utils.pdf_handler import pdf_to_base64, validate_pdf, get_pdf_info
from utils.claude_client import ClaudeRFPClient
from utils.pdf_generator import RFPAnalysisGenerator
from utils.excel_generator import RFPExcelGenerator
from prompts.rfp_prompts import get_rfp_analysis_prompt


# Page configuration
st.set_page_config(
    page_title="RFP Alignment Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def get_api_key() -> str:
    """
    Get API key from Streamlit secrets (Cloud) or environment (local).
    
    Returns:
        API key string
    """
    # Try Streamlit secrets first (Cloud deployment)
    if "ANTHROPIC_API_KEY" in st.secrets:
        return st.secrets["ANTHROPIC_API_KEY"]
    
    # Fall back to environment variables (local dev)
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        st.error("🔑 **API Key Not Found**")
        st.info("""
        **For local development:** Create a `.env` file with:
        ```
        ANTHROPIC_API_KEY=your_key_here
        ```
        
        **For Streamlit Cloud:** Add `ANTHROPIC_API_KEY` to your app secrets in settings.
        """)
        st.stop()
    
    return api_key


def validate_file_upload(uploaded_file) -> bool:
    """
    Validate uploaded file size and type.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        True if valid, False otherwise (displays error)
    """
    # Check file size (10MB limit)
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > 10:
        st.error(f"❌ File too large ({file_size_mb:.2f}MB). Maximum size is 10MB.")
        return False
    
    # Validate PDF
    is_valid, error_msg = validate_pdf(uploaded_file)
    if not is_valid:
        st.error(f"❌ {error_msg}")
        return False
    
    return True


def process_rfp(uploaded_file, claude_client):
    """
    Process RFP through full pipeline with progress tracking.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        claude_client: ClaudeRFPClient instance
    
    Returns:
        Tuple of (analysis_dict, pdf_buffer, excel_buffer) or (None, None, None) on error
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: PDF conversion
        status_text.text("📄 Converting PDF to base64...")
        progress_bar.progress(15)
        
        pdf_base64, page_count = pdf_to_base64(uploaded_file)
        st.success(f"✅ Loaded PDF with {page_count} pages")
        
        # Step 2: Claude analysis
        status_text.text("🤖 Analyzing RFP with Claude AI (this may take 20-40 seconds)...")
        progress_bar.progress(30)
        
        prompt = get_rfp_analysis_prompt()
        analysis = claude_client.analyze_rfp(pdf_base64, prompt)
        
        # Validate structure
        claude_client.validate_analysis_structure(analysis)
        progress_bar.progress(60)
        st.success("✅ Analysis complete!")
        
        # Step 3: Generate PDF report
        status_text.text("📝 Generating PDF analysis report...")
        progress_bar.progress(75)
        
        pdf_generator = RFPAnalysisGenerator()
        pdf_buffer = pdf_generator.generate_analysis_pdf(
            analysis,
            uploaded_file.name
        )
        
        # Step 4: Generate Excel workbook
        status_text.text("📊 Generating Excel alignment questions...")
        progress_bar.progress(90)
        
        excel_generator = RFPExcelGenerator()
        excel_buffer = excel_generator.generate_workbook(
            analysis.get("next_steps", []),
            analysis.get("alignment_questions", []),
            uploaded_file.name
        )
        
        progress_bar.progress(100)
        status_text.text("✅ All files generated successfully!")
        
        # Clear progress indicators after a moment
        import time
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return analysis, pdf_buffer, excel_buffer
    
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error during processing: {str(e)}")
        return None, None, None


def display_analysis_summary(analysis: dict):
    """
    Display analysis summary in expandable sections.
    
    Args:
        analysis: Dictionary with analysis results
    """
    st.subheader("📋 Analysis Summary")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Client Problems", len(analysis.get("client_problems", [])))
    with col2:
        st.metric("Requirements", len(analysis.get("requirements", [])))
    with col3:
        st.metric("Gotchas", len(analysis.get("gotchas", [])))
    with col4:
        st.metric("Timeline Events", len(analysis.get("timeline", [])))
    
    st.divider()
    
    # Expandable sections
    with st.expander("🎯 Client Problems", expanded=True):
        problems = analysis.get("client_problems", [])
        if problems:
            for i, problem in enumerate(problems, 1):
                st.write(f"{i}. {problem}")
        else:
            st.info("No client problems identified")
    
    with st.expander("📝 Specific Requirements"):
        requirements = analysis.get("requirements", [])
        if requirements:
            for i, req in enumerate(requirements, 1):
                st.write(f"{i}. {req}")
        else:
            st.info("No requirements identified")
    
    with st.expander("⚠️ Gotchas & Ambiguities"):
        gotchas = analysis.get("gotchas", [])
        if gotchas:
            for i, gotcha in enumerate(gotchas, 1):
                st.warning(f"{i}. {gotcha}")
        else:
            st.success("No major gotchas identified")
    
    with st.expander("📅 Timeline"):
        timeline = analysis.get("timeline", [])
        if timeline:
            for item in timeline:
                event = item.get("event", "Unknown")
                date = item.get("date", "TBD")
                st.write(f"**{event}:** {date}")
        else:
            st.info("No timeline information available")


def create_download_section(pdf_buffer, excel_buffer, filename: str):
    """
    Create download buttons for generated files.
    
    Args:
        pdf_buffer: BytesIO with PDF content
        excel_buffer: BytesIO with Excel content
        filename: Original RFP filename (for naming outputs)
    """
    st.subheader("⬇️ Download Results")
    
    # Generate clean filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = filename.replace(".pdf", "").replace(" ", "_")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Download PDF Analysis",
            data=pdf_buffer.getvalue(),
            file_name=f"{base_name}_analysis_{timestamp}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.caption("Structured analysis with client problems, requirements, gotchas, and timeline")
    
    with col2:
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_buffer.getvalue(),
            file_name=f"{base_name}_alignment_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.caption("Next steps and strategic alignment questions for your team")


def main():
    """Main application entry point."""
    
    # Header
    st.title("📄 RFP Alignment Assistant")
    st.markdown("""
    Upload an RFP PDF and get instant AI-powered analysis plus strategic alignment materials.
    Generate a structured analysis report and Excel workbook with next steps and key questions.
    """)
    
    # Get API key
    api_key = get_api_key()
    claude_client = ClaudeRFPClient(api_key)
    
    st.divider()
    
    # File upload section
    st.subheader("📤 Upload RFP")
    uploaded_file = st.file_uploader(
        "Choose a PDF file (max 10MB)",
        type=["pdf"],
        help="Upload the RFP document you want to analyze"
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        # Display file info
        pdf_info = get_pdf_info(uploaded_file)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filename", pdf_info["name"])
        with col2:
            st.metric("Pages", pdf_info["pages"])
        with col3:
            st.metric("Size", f"{pdf_info['size_mb']} MB")
        
        st.divider()
        
        # Validate file
        if not validate_file_upload(uploaded_file):
            return
        
        # Process button
        if st.button("🚀 Analyze RFP", type="primary", use_container_width=True):
            # Process the RFP
            analysis, pdf_buffer, excel_buffer = process_rfp(uploaded_file, claude_client)
            
            if analysis and pdf_buffer and excel_buffer:
                # Store in session state
                st.session_state.analysis = analysis
                st.session_state.pdf_buffer = pdf_buffer
                st.session_state.excel_buffer = excel_buffer
                st.session_state.filename = uploaded_file.name
        
        # Display results if available
        if "analysis" in st.session_state:
            st.divider()
            
            # Display summary
            display_analysis_summary(st.session_state.analysis)
            
            st.divider()
            
            # Download section
            create_download_section(
                st.session_state.pdf_buffer,
                st.session_state.excel_buffer,
                st.session_state.filename
            )
            
            st.divider()
            
            # Option to analyze another
            if st.button("📤 Analyze Another RFP"):
                # Clear session state
                for key in ["analysis", "pdf_buffer", "excel_buffer", "filename"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    else:
        # Show instructions when no file uploaded
        st.info("👆 Upload an RFP PDF to get started")
        
        with st.expander("ℹ️ What does this tool do?"):
            st.markdown("""
            **RFP Alignment Assistant** helps consulting teams by:
            
            1. **Extracting Key Information:**
               - Client problems and challenges
               - Specific requirements and deliverables
               - Red flags and ambiguities
               - Timeline and key dates
            
            2. **Generating Two Outputs:**
               - **PDF Report:** Structured analysis document
               - **Excel Workbook:** Next steps and strategic alignment questions
            
            3. **Saving Time:**
               - Instant analysis in 30-60 seconds
               - No manual reading and note-taking
               - Structured format for team discussions
            
            **Best For:** RFPs, RFIs, RFQs, and similar proposal requests
            """)


if __name__ == "__main__":
    main()
