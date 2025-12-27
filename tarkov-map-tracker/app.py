"""
Tarkov Interactive Map Tracker
Main Streamlit Application

Integrates screenshot parsing, log monitoring, and interactive maps.
"""

import streamlit as st
import os
import time
from pathlib import Path
import yaml

# Import our custom modules
from screenshot_parser import ScreenshotParser, get_latest_position
from log_monitor import TarkovLogMonitor, create_monitor
from tarkov_api import TarkovAPI, get_active_quests
from map_renderer import MapRenderer

# Page configuration
st.set_page_config(
    page_title="Tarkov Map Tracker",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark tactical theme
st.markdown("""
<style>
    .main {
        background-color: #1a1a1a;
    }
    .stButton>button {
        background-color: #4a4a4a;
        color: white;
    }
    .stSelectbox {
        color: white;
    }
    h1, h2, h3 {
        color: #00ff41;
        font-family: 'Courier New', monospace;
    }
    .position-display {
        background-color: #2a2a2a;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #00ff41;
        margin: 10px 0;
    }
    .quest-info {
        background-color: #2a2a2a;
        padding: 10px;
        border-left: 4px solid #0088ff;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_config():
    """Load configuration from config.yaml."""
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return None


@st.cache_resource
def get_api_client():
    """Get cached API client instance."""
    config = load_config()
    cache_ttl = 300
    if config and 'app' in config:
        cache_ttl = config['app'].get('cache_ttl', 300)
    return TarkovAPI(cache_ttl=cache_ttl)


def main():
    """Main application entry point."""
    
    # Title and header
    st.title("🗺️ Tarkov Interactive Map Tracker")
    st.markdown("---")
    
    # Load configuration
    config = load_config()
    
    # Initialize session state
    if 'current_position' not in st.session_state:
        st.session_state.current_position = None
    if 'current_map' not in st.session_state:
        st.session_state.current_map = config['app']['default_map'] if config else 'customs'
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False
    if 'show_quests' not in st.session_state:
        st.session_state.show_quests = True
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Path configuration
        st.subheader("File Paths")
        
        default_screenshot_path = config['eft']['screenshot_path'] if config else ""
        screenshot_path = st.text_input(
            "Screenshot Directory",
            value=default_screenshot_path,
            help="Path to your EFT screenshots folder"
        )
        
        default_log_path = config['eft']['log_path'] if config else ""
        log_path = st.text_input(
            "Log Directory",
            value=default_log_path,
            help="Path to EFT log files"
        )
        
        st.markdown("---")
        
        # Map selection
        st.subheader("Map Settings")
        
        api = get_api_client()
        available_maps = api.get_maps()
        map_names = [m['normalizedName'] for m in available_maps if m.get('normalizedName')]
        
        if map_names:
            current_map_index = map_names.index(st.session_state.current_map) if st.session_state.current_map in map_names else 0
            selected_map = st.selectbox(
                "Select Map",
                map_names,
                index=current_map_index,
                format_func=lambda x: x.title()
            )
            st.session_state.current_map = selected_map
        else:
            st.session_state.current_map = 'customs'
            st.warning("Could not load maps from API. Using Customs as default.")
        
        # Map level for multi-level maps
        map_level = st.selectbox(
            "Map Level",
            [1, 2, 3],
            index=0,
            help="Select floor level for multi-story maps"
        )
        
        st.markdown("---")
        
        # Display options
        st.subheader("Display Options")
        st.session_state.show_quests = st.checkbox("Show Quest Markers", value=True)
        
        st.markdown("---")
        
        # Auto-refresh control
        st.subheader("Live Tracking")
        st.session_state.auto_refresh = st.checkbox(
            "Auto-Refresh Position",
            value=st.session_state.auto_refresh,
            help="Automatically update position from latest screenshot"
        )
        
        if st.session_state.auto_refresh:
            refresh_interval = st.slider(
                "Refresh Interval (seconds)",
                min_value=1,
                max_value=10,
                value=config['app']['auto_refresh_interval'] if config else 2
            )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"📍 {st.session_state.current_map.title()} Map")
        
        # Manual position update button
        if st.button("🔄 Update Position from Screenshot"):
            if screenshot_path and os.path.exists(os.path.expandvars(screenshot_path)):
                position = get_latest_position(screenshot_path)
                if position:
                    st.session_state.current_position = position
                    st.success(f"Position updated! Found at ({position['x']:.1f}, {position['y']:.1f})")
                else:
                    st.warning("No valid position screenshot found.")
            else:
                st.error("Invalid screenshot path. Please configure in sidebar.")
        
        # Auto-refresh position
        if st.session_state.auto_refresh and screenshot_path:
            position = get_latest_position(screenshot_path)
            if position:
                st.session_state.current_position = position
            time.sleep(refresh_interval if 'refresh_interval' in locals() else 2)
            st.rerun()
        
        # Render map
        renderer = MapRenderer()
        
        # Get quest data if enabled
        quests = None
        if st.session_state.show_quests:
            quest_objectives = api.get_quest_objectives_with_locations(st.session_state.current_map)
            quests = quest_objectives
        
        # Create map
        map_obj = renderer.render_map(
            map_name=st.session_state.current_map,
            level=map_level,
            player_position=st.session_state.current_position,
            quests=quests
        )
        
        # Display map using streamlit-folium
        try:
            from streamlit_folium import st_folium
            st_folium(map_obj, width=900, height=600)
        except ImportError:
            # Fallback: display as HTML
            st.components.v1.html(map_obj._repr_html_(), height=600)
    
    with col2:
        st.header("📊 Status")
        
        # Current position display
        st.subheader("Current Position")
        if st.session_state.current_position:
            pos = st.session_state.current_position
            st.markdown(f"""
            <div class="position-display">
                <h3 style="margin-top: 0;">📍 Location</h3>
                <p><strong>X:</strong> {pos['x']:.2f}</p>
                <p><strong>Y:</strong> {pos['y']:.2f}</p>
                <p><strong>Z:</strong> {pos['z']:.2f}m</p>
                <p><strong>Facing:</strong> {pos['rotation']}°</p>
                <p style="font-size: 0.8em; color: #888;">From: {pos.get('filename', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No position data available. Take a screenshot in-game to track your position.")
        
        st.markdown("---")
        
        # Quest information
        st.subheader(f"🎯 {st.session_state.current_map.title()} Quests")
        
        if st.session_state.show_quests:
            quests = api.get_quests(st.session_state.current_map)
            
            if quests:
                st.write(f"**{len(quests)} quests** available on this map")
                
                # Show first few quests
                for quest in quests[:5]:
                    trader = quest.get('trader', {}).get('name', 'Unknown')
                    objectives_count = len(quest.get('objectives', []))
                    
                    with st.expander(f"{quest['name']} ({trader})"):
                        st.write(f"**Objectives:** {objectives_count}")
                        for obj in quest.get('objectives', [])[:3]:
                            st.markdown(f"""
                            <div class="quest-info">
                                <strong>{obj['type']}</strong><br>
                                {obj['description']}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No quests found for this map.")
        
        st.markdown("---")
        
        # Map info
        st.subheader("ℹ️ Map Information")
        map_data = api.get_map_data(st.session_state.current_map)
        if map_data:
            st.write(f"**Name:** {map_data['name']}")
            st.write(f"**Raid Duration:** {map_data.get('raidDuration', 'Unknown')} min")
            if map_data.get('description'):
                st.write(f"**Description:** {map_data['description']}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9em;">
        <p>Powered by <a href="https://tarkov.dev" target="_blank">tarkov.dev</a> API 
        and <a href="https://github.com/the-hideout" target="_blank">the-hideout</a> repositories</p>
        <p>GPL-3.0 License | Not affiliated with Battlestate Games</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
