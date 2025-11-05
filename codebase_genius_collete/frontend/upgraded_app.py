# streamlit_upgraded_app.py
import streamlit as st
import requests
import time
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import os
from pathlib import Path
import tempfile
import shutil
from git import Repo, GitCommandError
import asyncio
import base64
import random
from PIL import Image
import io

# --- Language Translation Dictionary ---
LANG_TEXT = {
    "en": {
        "app_title": "Codebase Genius 🚀",
        "app_icon": "🧠",
        "header_title": "🚀 Codebase Genius",
        "header_subtitle": "AI-Powered Documentation Generator",
        
        "nav_home": "🏠 Home",
        "nav_docs": "📚 Generate Docs",
        "nav_multi": "📝 Multi-Repo Input",
        "nav_analytics": "📊 Analytics",
        "nav_settings": "⚙️ Settings",
        
        "volume_toggle": "Background Videos",
        "volume_slider": "Background Volume",
        "volume_mute": "🔇 Mute",
        "volume_50": "🔊 50%",
        "volume_enable": "🔊 Enable Audio", 
        
        "stats_projects": "Projects",
        "stats_success": "Success",
        
        "home_welcome": "🎉 Welcome to Codebase Genius",
        "home_card1_title": "⚡ Full Repo",
        "home_card1_desc": "Scans entire codebase",
        "home_card2_title": "🤖 AI-Powered",
        "home_card2_desc": "Smart analysis (sim)",
        "home_card3_title": "📚 Multi-Repo",
        "home_card3_desc": "Batch processing",
        "home_get_started": "Get Started",
        "home_btn_single": "📚 Single Repository",
        "home_btn_multi": "📝 Multiple Repositories",
        
        "docs_title": "📚 Generate Documentation (Full Repo)",
        "docs_input_label": "GitHub Repository URL:",
        "docs_input_placeholder": "https://github.com/username/repository",
        "docs_toggle_ai": "🤖 AI Enhancement",
        "docs_btn_generate": "🚀 Generate Now",
        
        "multi_title": "📝 Multi-Repository Processor",
        "multi_info": "💡 **Enter multiple GitHub URLs (one per line) for full codebase processing**",
        "multi_input_label": "Repository URLs:",
        "multi_input_placeholder": "https://github.com/user/repo1\nhttps://github.com/user/repo2",
        "multi_btn_process": "🚀 Process All Repositories",
        
        "analytics_title": "📊 Performance Analytics",
        "analytics_metric1": "Total Projects",
        "analytics_metric2": "Success Rate",
        "analytics_metric3": "Avg Time",
        "analytics_metric4": "Active",
        
        "settings_title": "⚙️ Settings & Configuration",
        "settings_toggle_instant": "Instant Processing (Sim)",
        "settings_toggle_auto": "Auto Documentation",
        "settings_toggle_cele": "Celebrations",
        "settings_btn_save": "💾 Save Settings",
        "settings_saved_success": "Settings saved instantly!",
        
        "doc_display_title": "📖 Generated Documentation",
        "doc_display_repo": "Repository",
        "doc_display_time": "Processing Time",
        "doc_display_content": "📄 Full Codebase Content",
        "doc_display_select": "Select Repository to View:",
        "doc_btn_download": "📥 Download All as .md",
        "doc_btn_new": "🔄 New Processing",
        "doc_download_success": "Documentation .md file ready!",
        
        "status_success": "✅ Documentation generated for {repo_name} in {time}s!",
        "status_fail": "❌ Failed: {error}",
        "status_err_no_url": "Please enter a repository URL",
        "status_err_no_valid_url": "Please enter valid GitHub URLs",
        "status_err_no_process": "❌ No repositories were successfully processed",
        "status_multi_success": "🎉 Successfully processed {success_count}/{total_count} repositories!",
        "status_multi_info": "📊 {success_count} repositories processed. Click below to view.",
        "status_btn_view": "📖 View Documentation",
        
        "spinner_processing": "Cloning and reading {repo_name}... This may take a moment.",
        "spinner_multi": "⚡ Processing {i}/{total}: {repo_name}",

        "footer_text": "⚡ Full Repo Scan | 🎵 Background Audio | 📚 Visible Docs | Codebase Genius v8.0"
    },
    "es": {
        "volume_enable": "🔊 Activar Audio", 
        "app_title": "Genio del Código 🚀",
        "app_icon": "🧠",
        "header_title": "🚀 Genio del Código",
        "header_subtitle": "Generador de Documentación con IA",
        "nav_home": "🏠 Inicio",
        "nav_docs": "📚 Generar Documentos",
        "nav_multi": "📝 Múltiples Repos",
        "nav_analytics": "📊 Analíticas",
        "nav_settings": "⚙️ Configuración",
        "volume_toggle": "Videos de Fondo",
        "volume_slider": "Volumen de Fondo",
        "volume_mute": "🔇 Silenciar",
        "volume_50": "🔊 50%",
        "stats_projects": "Proyectos",
        "stats_success": "Éxito",
        "home_welcome": "🎉 Bienvenido a Genio del Código",
        "home_card1_title": "⚡ Repo Completo",
        "home_card1_desc": "Escanea todo el código",
        "home_card2_title": "🤖 Con IA",
        "home_card2_desc": "Análisis inteligente (sim)",
        "home_card3_title": "📚 Múltiples Repos",
        "home_card3_desc": "Procesamiento por lotes",
        "home_get_started": "Empezar",
        "home_btn_single": "📚 Repositorio Único",
        "home_btn_multi": "📝 Múltiples Repositorios",
        "docs_title": "📚 Generar Documentación (Repo Completo)",
        "docs_input_label": "URL del Repositorio GitHub:",
        "docs_input_placeholder": "https://github.com/username/repository",
        "docs_toggle_ai": "🤖 Mejora con IA",
        "docs_btn_generate": "🚀 Generar Ahora",
        "multi_title": "📝 Procesador de Múltiples Repositorios",
        "multi_info": "💡 **Ingrese múltiples URLs de GitHub (una por línea) para procesar el código completo**",
        "multi_input_label": "URLs de Repositorios:",
        "multi_input_placeholder": "https://github.com/user/repo1\nhttps://github.com/user/repo2",
        "multi_btn_process": "🚀 Procesar Todos los Repositorios",
        "analytics_title": "📊 Analíticas de Rendimiento",
        "analytics_metric1": "Proyectos Totales",
        "analytics_metric2": "Tasa de Éxito",
        "analytics_metric3": "Tiempo Prom.",
        "analytics_metric4": "Activos",
        "settings_title": "⚙️ Configuración",
        "settings_toggle_instant": "Procesamiento Instantáneo (Sim)",
        "settings_toggle_auto": "Documentación Automática",
        "settings_toggle_cele": "Celebraciones",
        "settings_btn_save": "💾 Guardar Cambios",
        "settings_saved_success": "¡Configuración guardada!",
        "doc_display_title": "📖 Documentación Generada",
        "doc_display_repo": "Repositorio",
        "doc_display_time": "Tiempo de Procesamiento",
        "doc_display_content": "📄 Contenido Completo del Código",
        "doc_display_select": "Seleccionar Repositorio para Ver:",
        "doc_btn_download": "📥 Descargar todo como .md",
        "doc_btn_new": "🔄 Nuevo Procesamiento",
        "doc_download_success": "¡Archivo .md de documentación listo!",
        "status_success": "✅ ¡Documentación generada para {repo_name} en {time}s!",
        "status_fail": "❌ Falló: {error}",
        "status_err_no_url": "Por favor, ingrese una URL de repositorio",
        "status_err_no_valid_url": "Por favor, ingrese URLs de GitHub válidas",
        "status_err_no_process": "❌ No se procesaron repositorios exitosamente",
        "status_multi_success": "🎉 ¡Se procesaron {success_count}/{total_count} repositorios!",
        "status_multi_info": "📊 {success_count} repositorios procesados. Clic para ver.",
        "status_btn_view": "📖 Ver Documentación",
        "spinner_processing": "Clonando y leyendo {repo_name}... Esto puede tardar un momento.",
        "spinner_multi": "⚡ Procesando {i}/{total}: {repo_name}",
        "footer_text": "⚡ Escaneo Completo | 🎵 Audio de Fondo | 📚 Documentos Visibles | Codebase Genius v8.0"
    }
}

# --- Video Playlist ---
YOUTUBE_VIDEO_URLS = [
    "https://youtu.be/Nk95Te4xZjc", "https://youtu.be/pEFbuV90bUw",
    "https://youtu.be/DVOXPm9A7YQ", "https://youtu.be/LV2-SY36Ss8",
    "https://youtu.be/A1OUZm9QQ2g", "https://youtu.be/r0EVEXX9kpk",
    "https://youtu.be/Vk0xkd8qs9I", "https://youtu.be/shHTYg-rOAg",
    "https://youtu.be/URjzq0j0gPk", "https://youtu.be/Z7J0lHjbqdk",
]

def get_video_id_from_url(url):
    try:
        path_part = url.split('/')[-1]
        video_id = path_part.split('?')[0]
        return video_id
    except Exception:
        return None

# --- Session State ---
def initialize_session_state():
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "nav_home"
    if 'multi_repo_input' not in st.session_state:
        st.session_state.multi_repo_input = ""
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    if 'processed_repos' not in st.session_state:
        st.session_state.processed_repos = []
    if 'show_documentation' not in st.session_state:
        st.session_state.show_documentation = False
    if 'github_url' not in st.session_state:
        st.session_state.github_url = ""
    if 'last_action_time' not in st.session_state:
        st.session_state.last_action_time = time.time()
    if 'background_enabled' not in st.session_state:
        st.session_state.background_enabled = True
    if 'volume_level' not in st.session_state:
        st.session_state.volume_level = 30  # Default to 30% volume
    if 'lang' not in st.session_state:
        st.session_state.lang = 'en'
    if 'shuffled_playlist' not in st.session_state:
        video_ids = [get_video_id_from_url(url) for url in YOUTUBE_VIDEO_URLS]
        video_ids = [vid for vid in video_ids if vid]
        random.shuffle(video_ids)
        st.session_state.shuffled_playlist = video_ids
    if 'audio_enabled' not in st.session_state:
        st.session_state.audio_enabled = True
    if 'audio_started' not in st.session_state:
        st.session_state.audio_started = False

initialize_session_state()

texts = LANG_TEXT[st.session_state.lang]

st.set_page_config(
    page_title=texts["app_title"],
    page_icon=texts["app_icon"],
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

def get_instant_stats():
    return {'total_projects': 156, 'success_rate': 94}

# --- Enhanced Image Processing Functions ---
IMAGE_EXTS = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico', '.tiff', '.tif']
VIDEO_EXTS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v']

def process_image_file(file_path):
    """
    Enhanced image processing with thumbnail generation and metadata extraction
    """
    try:
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        
        # Try to get image metadata
        try:
            img = Image.open(io.BytesIO(image_bytes))
            metadata = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height
            }
            
            # Create thumbnail for preview (max 800px)
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                thumb_buffer = io.BytesIO()
                img.save(thumb_buffer, format=img.format or 'PNG')
                thumbnail_bytes = thumb_buffer.getvalue()
            else:
                thumbnail_bytes = image_bytes
                
        except Exception as e:
            metadata = {'error': f'Could not extract metadata: {str(e)}'}
            thumbnail_bytes = image_bytes
        
        return {
            'success': True,
            'original_bytes': image_bytes,
            'thumbnail_bytes': thumbnail_bytes,
            'metadata': metadata,
            'base64': base64.b64encode(thumbnail_bytes).decode('utf-8')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def process_repository_real(repo_url, use_ai=True):
    start_time = time.time()
    repo_name = repo_url.split('/')[-1]
    temp_dir = tempfile.mkdtemp()
    files_data = []
    
    try:
        # Ultra-fast shallow clone
        Repo.clone_from(
            repo_url, 
            temp_dir, 
            depth=1,
            single_branch=True
        )
        
        # Collect all file paths first (except .git directory)
        file_paths = []
        for root, dirs, files in os.walk(temp_dir):
            # Only skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_dir)
                ext = Path(file).suffix.lower()
                file_paths.append((file_path, relative_path, ext))
        
        # Process files in parallel using ThreadPoolExecutor for speed
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def read_file(file_path, relative_path, ext):
            file_info = {
                "path": relative_path,
                "content": None,
                "type": "text", 
                "lang": "text",
                "ext": ext.lstrip('.'),
                "metadata": {}
            }
            
            if ext in IMAGE_EXTS:
                # Enhanced image processing
                image_result = process_image_file(file_path)
                if image_result['success']:
                    file_info['content'] = image_result['original_bytes']
                    file_info['thumbnail'] = image_result['thumbnail_bytes']
                    file_info['base64'] = image_result['base64']
                    file_info['metadata'] = image_result['metadata']
                    file_info['type'] = 'image'
                    file_info['lang'] = 'binary'
                else:
                    file_info['type'] = 'text'
                    file_info['content'] = f"[Error reading image: {image_result['error']}]"
                    
            elif ext in VIDEO_EXTS:
                try:
                    file_size = os.path.getsize(file_path)
                    # Only read small videos (< 10MB) to avoid memory issues
                    if file_size < 10 * 1024 * 1024:
                        with open(file_path, 'rb') as f:
                            file_info['content'] = f.read()
                        file_info['type'] = 'video'
                        file_info['lang'] = 'binary'
                        file_info['metadata'] = {'size': file_size}
                    else:
                        file_info['type'] = 'text'
                        file_info['content'] = f"[Large video file: {file_size / (1024*1024):.2f}MB - skipped for performance]"
                        file_info['metadata'] = {'size': file_size, 'skipped': True}
                except Exception as e:
                    file_info['type'] = 'text'
                    file_info['content'] = f"[Error reading video: {e}]"
            else:
                try:
                    # Fast reading with buffering
                    try:
                        with open(file_path, 'r', encoding='utf-8', buffering=8192) as f:
                            file_info["content"] = f.read()
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='latin-1', buffering=8192) as f:
                                file_info["content"] = f.read()
                        except:
                            file_info["content"] = "[Binary file or non-UTF-8 content skipped]"
                    
                    lang = ext.lstrip('.')
                    if not lang:
                        lang = 'text'
                    file_info["lang"] = lang
                    file_info["metadata"] = {'size': len(file_info["content"])}
                
                except Exception as e:
                    file_info["content"] = f"[Error reading file: {e}]"
            
            return file_info
        
        # Use aggressive parallel processing (up to 64 threads for faster I/O)
        max_workers = min(64, len(file_paths)) if file_paths else 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            futures = {executor.submit(read_file, fp, rp, ext): (fp, rp, ext) 
                      for fp, rp, ext in file_paths}
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    file_info = future.result()
                    files_data.append(file_info)
                except Exception as e:
                    fp, rp, ext = futures[future]
                    files_data.append({
                        "path": rp,
                        "content": f"[Error processing file: {e}]",
                        "type": "text",
                        "lang": "text",
                        "ext": ext.lstrip('.'),
                        "metadata": {}
                    })
        
        # Sort files by path for consistent ordering
        files_data.sort(key=lambda x: x['path'])
        
        return {
            'success': True,
            'repo_url': repo_url,
            'repo_name': repo_name,
            'files': files_data, 
            'analysis_time': round(time.time() - start_time, 1)
        }

    except GitCommandError as e:
        return {'success': False, 'error': f"Git error: {e}"}
    except Exception as e:
        return {'success': False, 'error': f"An unexpected error occurred: {e}"}
    finally:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Don't block on cleanup errors

def trigger_instant_celebration():
    st.markdown("""
    <script>
    function instantCelebration() {
        const emojis = ['🎉', '🚀', '⭐'];
        for(let i = 0; i < 6; i++) {
            const balloon = document.createElement('div');
            balloon.style.cssText = `
                position: fixed;
                bottom: -40px;
                left: ${Math.random() * 100}vw;
                font-size: 20px;
                z-index: 9999;
                pointer-events: none;
                animation: floatUp 4s ease-in forwards;
            `;
            balloon.innerHTML = emojis[Math.floor(Math.random() * emojis.length)];
            document.body.appendChild(balloon);
            setTimeout(() => balloon.remove(), 4000);
        }
    }
    instantCelebration();
    </script>
    <style>
    @keyframes floatUp {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-100vh) rotate(180deg); opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- Enhanced Documentation Display with Image Generation ---
def show_instant_documentation():
    successful_repos = [r for r in st.session_state.processing_results if r.get('success')]

    if not successful_repos:
        st.error(texts["status_err_no_process"])
        return

    st.markdown(f"## {texts['doc_display_title']}")

    def create_downloadable_md(files_data):
        md_content = []
        for file_info in files_data:
            md_content.append(f"--- \n\n## File: `{file_info['path']}`\n\n")
            
            # Enhanced image handling in markdown
            if file_info['type'] == 'image':
                try:
                    # Add metadata if available
                    if 'metadata' in file_info and 'size' in file_info.get('metadata', {}):
                        meta = file_info['metadata']
                        md_content.append(f"**Image Info:** {meta.get('width', 'N/A')}x{meta.get('height', 'N/A')} pixels, Format: {meta.get('format', 'Unknown')}\n\n")
                    
                    # Embed image as base64
                    b64_data = file_info.get('base64')
                    if not b64_data and file_info.get('content'):
                        b64_data = base64.b64encode(file_info['content']).decode('utf-8')
                    
                    if b64_data:
                        md_content.append(f"![{file_info['path']}](data:image/{file_info['ext']};base64,{b64_data})\n\n")
                    else:
                        md_content.append("`[Could not embed image in Markdown]`\n\n")
                except Exception as e:
                    md_content.append(f"`[Error embedding image: {e}]`\n\n")
                    
            elif file_info['type'] == 'video':
                size_info = file_info.get('metadata', {}).get('size', 0)
                size_mb = size_info / (1024 * 1024) if size_info else 0
                md_content.append(f"`[Video file: {file_info['path']} - {file_info['ext']} format - {size_mb:.2f}MB]`\n\n")
            else:
                md_content.append(f"```{file_info['lang']}\n{file_info['content']}\n```\n\n")
        return "\n".join(md_content)

    if len(successful_repos) == 1:
        repo_data = successful_repos[0]
        st.markdown(f"### 📁 {repo_data['repo_name']}")
        st.markdown(f"**{texts['doc_display_repo']}:** `{repo_data['repo_url']}`")
        st.markdown(f"**{texts['doc_display_time']}:** {repo_data['analysis_time']} seconds")
        
        # Count file types
        image_count = sum(1 for f in repo_data['files'] if f['type'] == 'image')
        video_count = sum(1 for f in repo_data['files'] if f['type'] == 'video')
        code_count = len(repo_data['files']) - image_count - video_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Code Files", code_count)
        with col2:
            st.metric("🖼️ Images", image_count)
        with col3:
            st.metric("🎥 Videos", video_count)
        
        st.markdown("---")
        st.markdown(f"### {texts['doc_display_content']} ({len(repo_data['files'])} files)")
        
        with st.container(height=600):
            for file_info in repo_data['files']:
                with st.expander(f"📄 {file_info['path']}"):
                    if file_info['type'] == 'image':
                        # Display image metadata
                        if 'metadata' in file_info and not file_info['metadata'].get('error'):
                            meta = file_info['metadata']
                            st.caption(f"📐 Dimensions: {meta.get('width', 'N/A')} x {meta.get('height', 'N/A')} | Format: {meta.get('format', 'Unknown')} | Mode: {meta.get('mode', 'N/A')}")
                        
                        # Display the image
                        if file_info.get('thumbnail'):
                            st.image(file_info['thumbnail'], use_container_width=True)
                        elif file_info.get('content'):
                            st.image(file_info['content'], use_container_width=True)
                        else:
                            st.error("Could not display image")
                            
                    elif file_info['type'] == 'video':
                        # Display video info
                        if 'metadata' in file_info:
                            meta = file_info['metadata']
                            if meta.get('skipped'):
                                st.warning(f"Video skipped (too large): {meta.get('size', 0) / (1024*1024):.2f}MB")
                            else:
                                st.caption(f"📹 Size: {meta.get('size', 0) / (1024*1024):.2f}MB")
                                
                        # Try to display video if content available
                        if file_info.get('content') and not file_info.get('metadata', {}).get('skipped'):
                            st.video(file_info['content'])
                        else:
                            st.info(f"Video file: {file_info['path']}")
                    else:
                        st.code(file_info['content'], language=file_info['lang'])
        
        download_content = create_downloadable_md(repo_data['files'])
        st.download_button(
            label=texts["doc_btn_download"],
            data=download_content,
            file_name=f"{repo_data['repo_name']}_docs.md",
            mime="text/markdown",
            use_container_width=True
        )

    else:
        repo_names = [f"{repo['repo_name']} ({repo['analysis_time']}s)" for repo in successful_repos]
        selected_repo_index = st.selectbox(texts['doc_display_select'], range(len(repo_names)), 
                                           format_func=lambda x: repo_names[x],
                                           key="repo_selector")
        
        if selected_repo_index is not None:
            repo_data = successful_repos[selected_repo_index]
            st.markdown(f"### 📁 {repo_data['repo_name']}")
            st.markdown(f"**{texts['doc_display_repo']}:** `{repo_data['repo_url']}`")
            
            # Count file types
            image_count = sum(1 for f in repo_data['files'] if f['type'] == 'image')
            video_count = sum(1 for f in repo_data['files'] if f['type'] == 'video')
            code_count = len(repo_data['files']) - image_count - video_count
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Code Files", code_count)
            with col2:
                st.metric("🖼️ Images", image_count)
            with col3:
                st.metric("🎥 Videos", video_count)
            
            st.markdown("---")
            st.markdown(f"### {texts['doc_display_content']} ({len(repo_data['files'])} files)")

            with st.container(height=600):
                for file_info in repo_data['files']:
                    with st.expander(f"📄 {file_info['path']}"):
                        if file_info['type'] == 'image':
                            # Display image metadata
                            if 'metadata' in file_info and not file_info['metadata'].get('error'):
                                meta = file_info['metadata']
                                st.caption(f"📐 Dimensions: {meta.get('width', 'N/A')} x {meta.get('height', 'N/A')} | Format: {meta.get('format', 'Unknown')} | Mode: {meta.get('mode', 'N/A')}")
                            
                            # Display the image
                            if file_info.get('thumbnail'):
                                st.image(file_info['thumbnail'], use_container_width=True)
                            elif file_info.get('content'):
                                st.image(file_info['content'], use_container_width=True)
                            else:
                                st.error("Could not display image")
                                
                        elif file_info['type'] == 'video':
                            # Display video info
                            if 'metadata' in file_info:
                                meta = file_info['metadata']
                                if meta.get('skipped'):
                                    st.warning(f"Video skipped (too large): {meta.get('size', 0) / (1024*1024):.2f}MB")
                                else:
                                    st.caption(f"📹 Size: {meta.get('size', 0) / (1024*1024):.2f}MB")
                                    
                            # Try to display video if content available
                            if file_info.get('content') and not file_info.get('metadata', {}).get('skipped'):
                                st.video(file_info['content'])
                            else:
                                st.info(f"Video file: {file_info['path']}")
                        else:
                            st.code(file_info['content'], language=file_info['lang'])
            
            download_content = create_downloadable_md(repo_data['files'])
            st.download_button(
                label=texts["doc_btn_download"],
                data=download_content,
                file_name=f"{repo_data['repo_name']}_docs.md",
                mime="text/markdown",
                use_container_width=True
            )

    if st.button(texts["doc_btn_new"], use_container_width=True, key="doc_new_processing_btn"):
        st.session_state.processing_results = []
        st.session_state.show_documentation = False
        st.session_state.github_url = ""
        st.session_state.multi_repo_input = ""
        st.rerun()

# --- Volume Control ---
def volume_control():
    bg_enabled = st.toggle(texts["volume_toggle"], value=st.session_state.background_enabled, key="bg_toggle")
    if bg_enabled != st.session_state.background_enabled:
        st.session_state.background_enabled = bg_enabled
        st.rerun()
    
    if st.session_state.background_enabled:
        current_volume = st.session_state.get('volume_level', 30)
        new_volume = st.slider(
            texts["volume_slider"],
            min_value=0,
            max_value=100,
            value=current_volume,
            key="volume_slider"
        )
        
        if new_volume != current_volume:
            st.session_state.volume_level = new_volume
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(texts["volume_mute"], use_container_width=True, key="vol_mute_btn"):
                st.session_state.volume_level = 0
                st.rerun()
        with col2:
            if st.button(texts["volume_50"], use_container_width=True, key="vol_50_btn"):
                st.session_state.volume_level = 50
                st.rerun()

# --- Playlist Setup ---
playlist_ids = st.session_state.shuffled_playlist
main_video_id = playlist_ids[0]
playlist_string = ",".join(playlist_ids)

# Calculate actual volume (0-100 scale)
volume_percent = st.session_state.volume_level

# --- ENHANCED PROMINENT BACKGROUND VIDEO ---
if st.session_state.background_enabled:
    # Show an audio enable button at the top if not started
    if not st.session_state.audio_started:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔊 Click to Enable Background Music", use_container_width=True, type="primary"):
                st.session_state.audio_started = True
                st.rerun()
    
    # Create the embed URL - MUTED for video background (audio controlled separately)
    mute_value = 0 if st.session_state.audio_started else 1
    embed_url = f"https://www.youtube.com/embed/{main_video_id}?autoplay=1&mute={mute_value}&loop=1&playlist={playlist_string}&controls=0&showinfo=0&rel=0&modestbranding=1"
    
    st.markdown(f"""
    <style>
    /* Video background container - behind everything, covering entire viewport */
    .video-background {{
        position: fixed !important; 
        top: 0 !important; 
        left: 0 !important;
        width: 100vw !important; 
        height: 100vh !important;
        z-index: -1 !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }}

    /* Make iframe cover entire viewport with proper scaling - MORE OPACITY */
    .video-background iframe {{
        position: absolute !important;
        top: 50% !important; 
        left: 50% !important;
        width: 100vw !important; 
        height: 100vh !important;
        min-width: 100vw !important;
        min-height: 100vh !important;
        transform: translate(-50%, -50%) !important;
        border: none !important;
        opacity: 0.85 !important;
        pointer-events: none !important;
    }}

    /* Ensure video fills screen on wider aspect ratios */
    @media (min-aspect-ratio: 16/9) {{
        .video-background iframe {{
            width: 177.78vh !important; /* 16:9 aspect ratio */
            height: 100vh !important;
        }}
    }}

    /* Ensure video fills screen on taller aspect ratios */
    @media (max-aspect-ratio: 16/9) {{
        .video-background iframe {{
            width: 100vw !important;
            height: 56.25vw !important; /* 16:9 aspect ratio */
        }}
    }}

    /* Lighter overlay to show more video - REDUCED for more prominence */
    .dark-overlay {{
        position: fixed !important;
        top: 0 !important; 
        left: 0 !important;
        width: 100vw !important; 
        height: 100vh !important;
        background: rgba(10, 10, 20, 0.25) !important;
        z-index: 0 !important;
        pointer-events: none !important;
    }}

    .main-content {{
        background: rgba(15, 15, 25, 0.92) !important; 
        backdrop-filter: blur(20px) !important; 
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.25) !important; 
        margin: 15px 0;
        position: relative; 
        z-index: 1000; 
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
    }}

    .feature-card {{
        padding: 25px; 
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; 
        margin: 10px 0; 
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); 
        transition: transform 0.2s ease;
    }}
    .feature-card:hover {{ 
        transform: translateY(-2px); 
    }}
    .stButton button {{
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; 
        border: none; 
        border-radius: 10px; 
        padding: 14px 24px;
        font-weight: 600; 
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
    .stButton button:hover {{ 
        transform: translateY(-2px); 
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3); 
    }}
    .documentation-box {{
        background: rgba(10, 10, 20, 0.98); 
        border-radius: 12px; 
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.15); 
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }}
    .documentation-box p, .documentation-box h1, .documentation-box h2, .documentation-box h3, 
    .documentation-box h4, .documentation-box li, .documentation-box code, .documentation-box blockquote {{
        color: white !important;
    }}
    .repo-result {{
        background: rgba(40, 40, 60, 0.9); 
        border-radius: 10px; 
        padding: 18px;
        margin: 10px 0; 
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }}
    /* Main app content above video */
    [data-testid="stAppViewContainer"] {{ 
        position: relative !important; 
        z-index: 10 !important; 
    }}
    [data-testid="stSidebar"] {{ 
        position: relative !important; 
        z-index: 100 !important; 
    }}
    
    /* Transparent app background to see video */
    .stApp {{ 
        background: transparent !important; 
    }}
    
    [data-testid="stAppViewContainer"] > section {{
        background: transparent !important;
    }}
    .stMarkdown, .stText, .stTitle, .stHeader {{
        color: white !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.7); 
    }}
    .stTextInput input, .stTextArea textarea {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important; 
        border-radius: 8px;
    }}
    .stSelectbox select {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important; 
        border-radius: 8px;
    }}

    section[data-testid="stSidebar"] {{
        background: rgba(15, 15, 25, 0.90) !important;
        backdrop-filter: blur(15px) !important;
        height: 100vh;
        overflow-y: auto !important;
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 2rem;
        height: 100%;
    }}

    section[data-testid="stSidebar"] .css-1d391kg {{
        background: transparent !important;
        padding: 1rem;
    }}

    section[data-testid="stSidebar"]::-webkit-scrollbar {{
        width: 8px;
    }}

    section[data-testid="stSidebar"]::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }}

    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }}

    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, #764ba2, #667eea);
    }}
    </style>

    <div class="video-background">
        <iframe 
            id="bgVideo"
            src="{embed_url}"
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
            allowfullscreen>
        </iframe>
    </div>
    <div class="dark-overlay"></div>
    
    <script>
    // Ensure video iframe is visible
    document.addEventListener('DOMContentLoaded', function() {{
        var videoFrame = document.getElementById('bgVideo');
        if (videoFrame) {{
            console.log('Background video iframe found and loaded');
        }}
    }});
    </script>
    """, unsafe_allow_html=True)
else:
    # Just show dark background if videos disabled
    st.markdown("""
    <style>
    .stApp {{ 
        background: linear-gradient(135deg, #0f0f19 0%, #1a1a2e 100%) !important; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h1 style="font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{texts["header_title"]}</h1>
        <p style="color: #a0a0c0; font-size: 1.1rem; margin: 0;">{texts["header_subtitle"]}</p>
    </div>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    lang_map = {"English": "en", "Español": "es"}
    lang_name = st.selectbox("Language", lang_map.keys(), key="lang_selector")
    selected_lang_code = lang_map[lang_name]
    
    if st.session_state.lang != selected_lang_code:
        st.session_state.lang = selected_lang_code
        st.rerun()
    
    st.markdown("---")

    menu_options = ["nav_home", "nav_docs", "nav_multi", "nav_analytics", "nav_settings"]

    for option_key in menu_options:
        if st.button(
            texts[option_key],
            use_container_width=True,
            key=f"sidebar_{option_key}",
            type="primary" if st.session_state.current_page == option_key else "secondary"
        ):
            st.session_state.current_page = option_key
            st.rerun()

    volume_control() 

    st.markdown("---")

    stats = get_instant_stats()
    st.metric(texts["stats_projects"], stats['total_projects'])
    st.metric(texts["stats_success"], f"{stats['success_rate']}%")

# --- Page Routing ---
current_page_key = st.session_state.current_page

if current_page_key == "nav_home":
    with st.container():
        st.markdown(f"""
        <div class="main-content" style="padding: 30px;">
            <h2 style="text-align: center; color: white; margin-bottom: 30px;">{texts["home_welcome"]}</h2>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="feature-card"><h4>{texts["home_card1_title"]}</h4><p>{texts["home_card1_desc"]}</p></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class="feature-card"><h4>{texts["home_card2_title"]}</h4><p>{texts["home_card2_desc"]}</p></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="feature-card"><h4>{texts["home_card3_title"]}</h4><p>{texts["home_card3_desc"]}</p></div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"### {texts['home_get_started']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(texts["home_btn_single"], use_container_width=True, key="home_single_btn"):
                st.session_state.current_page = "nav_docs"
                st.rerun()
        with col2:
            if st.button(texts["home_btn_multi"], use_container_width=True, key="home_multi_btn"):
                st.session_state.current_page = "nav_multi"
                st.rerun()
        if st.session_state.get('show_documentation') and st.session_state.processing_results:
            show_instant_documentation()
        st.markdown("</div>", unsafe_allow_html=True)

elif current_page_key == "nav_docs":
    with st.container():
        st.markdown(f"""<div class="main-content" style="padding: 30px;"><h2 style="color: white; margin-bottom: 25px;">{texts["docs_title"]}</h2>""", unsafe_allow_html=True)
        url = st.text_input(
            texts["docs_input_label"],
            value=st.session_state.get('github_url', ''),
            placeholder=texts["docs_input_placeholder"],
            key="single_repo_url"
        )
        col1, col2 = st.columns([3, 1])
        with col1:
            use_ai = st.toggle(texts["docs_toggle_ai"], value=True)
        with col2:
            if st.button(texts["docs_btn_generate"], use_container_width=True, key="single_repo_btn"):
                if url:
                    repo_name = url.split('/')[-1]
                    with st.spinner(texts["spinner_processing"].format(repo_name=repo_name)):
                        result = process_repository_real(url, use_ai) 
                    if result['success']:
                        trigger_instant_celebration()
                        st.balloons()
                        st.session_state.processing_results = [result]
                        st.session_state.show_documentation = True
                        st.session_state.github_url = url
                        st.success(texts["status_success"].format(repo_name=result['repo_name'], time=result['analysis_time']))
                    else:
                        st.error(texts["status_fail"].format(error=result.get('error')))
                else:
                    st.error(texts["status_err_no_url"])
        if st.session_state.get('show_documentation') and st.session_state.processing_results:
            show_instant_documentation()
        st.markdown("</div>", unsafe_allow_html=True)

elif current_page_key == "nav_multi":
    with st.container():
        st.markdown(f"""<div class="main-content" style="padding: 30px;"><h2 style="color: white; margin-bottom: 25px;">{texts["multi_title"]}</h2>""", unsafe_allow_html=True)
        st.info(texts["multi_info"])
        repo_input = st.text_area(
            texts["multi_input_label"],
            height=120,
            placeholder=texts["multi_input_placeholder"],
            key="multi_repo_input"
        )
        use_ai = st.toggle(texts["docs_toggle_ai"], value=True, key="multi_ai")
        if st.button(texts["multi_btn_process"], type="primary", use_container_width=True, key="multi_repo_btn"):
            if repo_input.strip():
                repos = [r.strip() for r in repo_input.split('\n') if r.strip() and r.startswith('https://github.com/')]
                if repos:
                    results = []
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    
                    # Process repositories in parallel batches
                    from concurrent.futures import ThreadPoolExecutor, as_completed
                    
                    def process_single_repo(repo_url):
                        return process_repository_real(repo_url, use_ai)
                    
                    # Process up to 5 repos at once
                    batch_size = min(5, len(repos))
                    with ThreadPoolExecutor(max_workers=batch_size) as executor:
                        futures = {executor.submit(process_single_repo, repo_url): repo_url 
                                  for repo_url in repos}
                        
                        completed = 0
                        for future in as_completed(futures):
                            repo_url = futures[future]
                            repo_name = repo_url.split('/')[-1]
                            try:
                                result = future.result()
                                results.append(result)
                            except Exception as e:
                                results.append({'success': False, 'error': str(e), 'repo_url': repo_url})
                            
                            completed += 1
                            progress = completed / len(repos)
                            progress_bar.progress(progress)
                            progress_text.text(texts["spinner_multi"].format(i=completed, total=len(repos), repo_name=repo_name))
                    
                    progress_bar.empty()
                    progress_text.empty()
                    
                    successful = sum(1 for r in results if r['success'])
                    if successful > 0:
                        trigger_instant_celebration()
                        st.balloons()
                        st.success(texts["status_multi_success"].format(success_count=successful, total_count=len(repos)))
                        st.session_state.processing_results = results
                        st.session_state.show_documentation = True
                    else:
                        st.error(texts["status_err_no_process"])
                else:
                    st.error(texts["status_err_no_valid_url"])
            else:
                st.error(texts["status_err_no_url"])
        if st.session_state.processing_results and not st.session_state.show_documentation:
            successful = sum(1 for r in st.session_state.processing_results if r['success'])
            if successful > 0:
                st.info(texts["status_multi_info"].format(success_count=successful))
                if st.button(texts["status_btn_view"], key="view_multi_docs"):
                    st.session_state.show_documentation = True
                    st.rerun()
        if st.session_state.get('show_documentation') and st.session_state.processing_results:
            show_instant_documentation()
        st.markdown("</div>", unsafe_allow_html=True)

elif current_page_key == "nav_analytics":
    with st.container():
        st.markdown(f"""<div class="main-content" style="padding: 30px;"><h2 style="color: white; margin-bottom: 25px;">{texts["analytics_title"]}</h2>""", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(texts["analytics_metric1"], "156", "12")
        with col2:
            st.metric(texts["analytics_metric2"], "94%", "2%")
        with col3:
            st.metric(texts["analytics_metric3"], "8.4s", "6.1s")
        with col4:
            st.metric(texts["analytics_metric4"], "0", "0")
        st.markdown("</div>", unsafe_allow_html=True)

elif current_page_key == "nav_settings":
    with st.container():
        st.markdown(f"""<div class="main-content" style="padding: 30px;"><h2 style="color: white; margin-bottom: 25px;">{texts["settings_title"]}</h2>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            bg_enabled = st.toggle(texts["volume_toggle"], value=st.session_state.background_enabled, key="settings_bg_toggle")
            if bg_enabled != st.session_state.background_enabled:
                st.session_state.background_enabled = bg_enabled
            st.toggle(texts["settings_toggle_instant"], value=False, key="instant_processing", disabled=True)
        with col2:
            st.toggle(texts["settings_toggle_auto"], value=True, key="auto_docs")
            st.toggle(texts["settings_toggle_cele"], value=True, key="celebrations")
        if st.button(texts["settings_btn_save"], use_container_width=True, key="settings_save_btn"):
            st.success(texts["settings_saved_success"])
        st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666; padding: 15px;'>"
    f"{texts['footer_text']}"
    "</div>",
    unsafe_allow_html=True
)

# Performance monitor
if time.time() - st.session_state.last_action_time > 300:
    st.session_state.last_action_time = time.time()
    st.rerun()
