# streamlit_enhanced.py
import streamlit as st
import requests
import time
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import os # Import os to check for file
from pathlib import Path # Import Path for file operations

# Page configuration
st.set_page_config(
    page_title="Codebase Genius 🚀",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    body {
        font-family: 'Roboto', sans-serif;
        background-color: #121212; /* CHANGED: Dark background */
        color: #e0e0e0; /* CHANGED: Light text for body */
    }

    /* --- Sidebar Style --- */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e; /* CHANGED: Dark sidebar */
        border-right: 1px solid #333;
    }
    
    /* --- 
    FIX: Force all text inside the sidebar to be light-colored 
    to solve the readability issue from the screenshot.
    --- */
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important; 
    }
    /* --- END OF FIX --- */

    /* --- Main Header --- */
    .main-header {
        font-size: 3.5rem; /* Slightly larger */
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        /* Red Gradient Text */
        background: linear-gradient(135deg, #c0392b 0%, #922b21 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }
    
    /* Sub-header */
    h3 {
        text-align: center;
        color: #aaa; /* CHANGED: Light gray for sub-headers */
        font-weight: 300;
        margin-bottom: 2rem;
    }
    
    /* Make all headers white */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    
    /* --- Notification Boxes --- */
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
        color: #155724; /* Dark text for light box */
    }
    .error-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
        color: #721c24; /* Dark text for light box */
    }

    /* --- Feature Cards (Home Page) --- */
    .feature-card {
        padding: 25px;
        border-radius: 12px;
        background: linear-gradient(135deg, #c0392b 0%, #922b21 100%);
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    .feature-card h3 {
        text-align: left;
        color: white;
        font-weight: 700;
    }

    /* --- Modern Card Styling for Forms/Expanders --- */
    [data-testid="stForm"], [data-testid="stExpander"] {
        background-color: #1e1e1e; /* CHANGED: Dark card background */
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #333; /* CHANGED: Darker border */
    }
    
    /* --- Themed Buttons --- */
    [data-testid="stButton"] button {
        background-color: #c0392b;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        transition: background-color 0.2s ease, transform 0.2s ease;
    }
    [data-testid="stButton"] button:hover {
        background-color: #922b21;
        transform: translateY(-2px);
    }
    [data-testid="stFormSubmitButton"] button {
        width: 100%;
        font-size: 1.1rem;
        padding: 12px;
    }
    [data-testid="stDownloadButton"] button {
        background-color: #27ae60;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #219150;
    }

    /* --- Documentation Dark Mode (Already correct) --- */
    .documentation-output {
        padding: 25px;
        border-radius: 10px;
        background-color: #1e1e1e; /* Dark background */
        border: 1px solid #444;    /* Darker border */
        color: #e0e0e0;           /* Light text */
        margin-top: 20px;
    }
    .documentation-output h1,
    .documentation-output h2,
    .documentation-output h3,
    .documentation-output h4 {
        color: #ffffff; /* Pure white for headers */
        border-bottom: 1px solid #555;
        padding-bottom: 5px;
    }
    .documentation-output code {
        background-color: #333; /* Darker code background */
        color: #f1f1f1;       /* Light code text */
        border-radius: 4px;
        padding: 2px 5px;
    }
    .documentation-output pre {
        background-color: #2b2b2b;
        color: #f1f1f1;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
    }
    
    /* --- Footer --- */
    footer {
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<h1 class="main-header">🚀 Codebase Genius</h1>', unsafe_allow_html=True)
    st.markdown("<h3>AI-Powered Documentation Generator</h3>", unsafe_allow_html=True)
    st.markdown("---")

# Sidebar
with st.sidebar:
    # --- THIS IS THE NEW ICON ---
    st.image("https://img.icons8.com/fluency/96/brain.png", width=100)
    # --- END OF CHANGE ---
    st.title("Navigation")
    
    menu = st.radio("Choose Action", [
        "🏠 Home", 
        "📚 Generate Docs", 
        "📊 Analytics", 
        "🔄 Recent Projects",
        "⚙️ Settings"
    ])
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Stats")
    # You can add real stats here from your API
    st.metric("Projects Processed", "15", "3")
    st.metric("Success Rate", "92%", "2%")
    st.metric("Avg Processing Time", "45s", "-5s")

# Home Page
if menu == "🏠 Home":
    st.markdown("## Welcome to Codebase Genius! 🎉")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered</h3>
            <p>Smart documentation with AI analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ Fast</h3>
            <p>Generate docs in seconds</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Accurate</h3>
            <p>Precise code analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo section
    st.markdown("## 🎬 Quick Start")
    with st.expander("Click here to try with a demo repository"):
        if st.button("🚀 Generate Demo Documentation"):
            with st.spinner("Generating documentation for demo repository..."):
                # You can pre-populate with a demo repo
                st.session_state.github_url = "https://github.com/Collete03/C.O.R.I.A.N"
                st.success("Demo repository loaded! Go to 'Generate Docs' tab.")

# Generate Documentation Page
elif menu == "📚 Generate Docs":
    st.markdown("## 📚 Generate Documentation")
    
    # Input form with better styling
    with st.form("doc_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            github_url = st.text_input(
                "🔗 GitHub Repository URL",
                placeholder="https://github.com/username/repository",
                value=st.session_state.get('github_url', '')
            )
        
        with col2:
            use_llm = st.toggle("🤖 AI Enhancement", value=True)
        
        submitted = st.form_submit_button("🚀 Generate Documentation", use_container_width=True)
    
    if submitted and github_url:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        steps = ["Cloning Repository", "Analyzing Code", "Generating Documentation", "Finalizing"]
        
        try:
            # Simulate progress (you can replace with real progress from your API)
            for i, step in enumerate(steps):
                status_text.text(f"🔄 {step}...")
                progress_bar.progress((i + 1) * 25)
                time.sleep(1)  # Simulate work
            
            # Make API call
            response = requests.post(
                "http://localhost:8000/generate", # Make sure this matches your server.py port
                json={"github_url": github_url, "use_llm": use_llm}
            )
            
            if response.status_code == 200:
                result = response.json()
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                
                # Success display
                st.markdown(f"""
                <div class="success-box">
                    <h3>🎉 Documentation Generated Successfully!</h3>
                    <p><strong>Repository:</strong> {result.get('repo_name', 'N/A')}</p>
                    <p><strong>Output Path:</strong> {result.get('output_path', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # --- THIS IS THE FIX ---
                # Load and display the documentation
                doc_path_str = result.get('output_path')
                doc_path = None # Initialize doc_path
                
                if doc_path_str:
                    # The server sends the *directory*, but we need the *file* inside it.
                    # Based on documentation_pipeline.py, the file is 'comprehensive_documentation.md'
                    output_dir_path = Path(doc_path_str)
                    doc_path = output_dir_path / "comprehensive_documentation.md" # This is the full file path
                    
                    if doc_path.exists():
                        st.markdown("---")
                        st.markdown("## 📄 Generated Documentation")
                        
                        try:
                            doc_content = doc_path.read_text(encoding="utf-8")
                            # Display in a styled container
                            st.markdown(f'<div class="documentation-output">{doc_content}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error reading documentation file: {e}")
                    else:
                        st.error(f"Could not find documentation file at: {doc_path.resolve()}")
                        st.info("Please check the `output_path` in your server's response and the expected filename.")
                
                # --- END OF FIX ---

                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    # Implement download functionality (NOW USES THE FIXED doc_path)
                    if doc_path and doc_path.exists(): # Use the new doc_path variable
                        with open(doc_path, "r", encoding="utf-8") as f:
                            st.download_button(
                                label="📥 Download .md",
                                data=f.read(),
                                file_name=f"{result.get('repo_name', 'docs')}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                
                with col2:
                    if st.button("🔄 Generate Another", use_container_width=True):
                        st.rerun()
                        
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ Error Generating Documentation</h3>
                    <p><strong>Status Code:</strong> {response.status_code}</p>
                    <pre>{response.text}</pre>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f"""
            <div class.error-box">
                <h3>❌ Connection Error</h3>
                <p>Could not connect to the server at http://localhost:8000. Is it running?</p>
                <p><strong>Error:</strong> {str(e)}</p>
            </div>
            """, unsafe_allow_html=True)

# Analytics Page
elif menu == "📊 Analytics":
    st.markdown("## 📊 Project Analytics")
    
    # Sample analytics data (replace with real data from your API)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = 15,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Total Projects"},
            delta = {'reference': 12},
            gauge = {'axis': {'range': [None, 20]}}
        )), use_container_width=True)
    
    with col2:
        st.plotly_chart(go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 92,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Success Rate %"},
            gauge = {'axis': {'range': [0, 100]}}
        )), use_container_width=True)
    
    with col3:
        st.plotly_chart(go.Figure(go.Indicator(
            mode = "number+delta",
            value = 45,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Avg Time (seconds)"},
            delta = {'reference': 50}
        )), use_container_width=True)
    
    # Language distribution chart
    st.markdown("### 📈 Language Distribution")
    languages = ['Python', 'JavaScript', 'Java', 'C++', 'Other']
    counts = [45, 30, 15, 7, 3]
    
    fig = px.pie(values=counts, names=languages, title="Projects by Language")
    st.plotly_chart(fig, use_container_width=True)

# Recent Projects Page
elif menu == "🔄 Recent Projects":
    st.markdown("## 🔄 Recent Projects")
    
    # Sample recent projects (replace with real data from your API)
    projects = [
        {"name": "C.O.R.I.A.N", "date": "2024-01-15", "status": "✅ Complete", "language": "Python"},
        {"name": "React-App", "date": "2024-01-14", "status": "✅ Complete", "language": "JavaScript"},
        {"name": "Data-Pipeline", "date": "2024-01-13", "status": "🔄 Processing", "language": "Python"},
        {"name": "Mobile-App", "date": "2024-01-12", "status": "✅ Complete", "language": "Java"},
    ]
    
    for project in projects:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{project['name']}**")
            with col2:
                st.write(project['date'])
            with col3:
                st.write(project['status'])
            with col4:
                st.write(project['language'])
            st.markdown("---")

# Settings Page
elif menu == "⚙️ Settings":
    st.markdown("## S️ Settings")
    
    with st.form("settings_form"):
        st.markdown("### API Configuration")
        api_url = st.text_input("API Base URL", value="http://localhost:8000")
        
        st.markdown("### Generation Options")
        col1, col2 = st.columns(2)
        with col1:
            auto_download = st.checkbox("Auto-download after generation", value=True)
            include_diagrams = st.checkbox("Include architecture diagrams", value=True)
        with col2:
            dark_mode = st.checkbox("Dark mode", value=False)
            notifications = st.checkbox("Enable notifications", value=True)
        
        if st.form_submit_button("💾 Save Settings", use_container_width=True):
            st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "Made with ❤️ using Streamlit | Codebase Genius v2.0"
    "</div>", 
    unsafe_allow_html=True
)





