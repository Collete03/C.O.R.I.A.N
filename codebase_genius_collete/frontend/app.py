# streamlit_enhanced.py
import streamlit as st
import requests
import time
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

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
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .error-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    .info-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 10px 0;
    }
    .feature-card {
        padding: 15px;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<h1 class="main-header">🚀 Codebase Genius</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Documentation Generator")
    st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
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
                "http://localhost:8000/generate",
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
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📖 View Documentation", use_container_width=True):
                        st.switch_page("View Documentation")  # You'd need to implement this page
                
                with col2:
                    if st.button("📥 Download", use_container_width=True):
                        # Implement download functionality
                        pass
                
                with col3:
                    if st.button("🔄 Generate Another", use_container_width=True):
                        st.rerun()
                        
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ Error Generating Documentation</h3>
                    <p>{response.text}</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <h3>❌ Connection Error</h3>
                <p>Could not connect to the server: {str(e)}</p>
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
    st.markdown("## ⚙️ Settings")
    
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
    "<div style='text-align: center; color: #666;'>"
    "Made with ❤️ using Streamlit | Codebase Genius v2.0"
    "</div>", 
    unsafe_allow_html=True
)