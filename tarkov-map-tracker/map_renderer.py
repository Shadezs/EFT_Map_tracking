"""
Map Renderer
Renders interactive Tarkov maps using Folium with SVG overlays.

Integrates with tarkov-dev-svg-maps for map data.
"""

import folium
from folium import plugins
from typing import Dict, List, Optional, Tuple, Any
import os
import json


class MapRenderer:
    """Renders interactive maps with position markers and quest overlays."""
    
    # Map bounds calibration (lat/lon coordinates)
    # These need to be calibrated based on actual game coordinates
    MAP_BOUNDS = {
        'customs': {
            'min_lat': -90.0,
            'max_lat': 90.0,
            'min_lon': -180.0,
            'max_lon': 180.0,
            'center': [0.0, 0.0],
            'zoom': 3
        },
        'woods': {
            'min_lat': -90.0,
            'max_lat': 90.0,
            'min_lon': -180.0,
            'max_lon': 180.0,
            'center': [0.0, 0.0],
            'zoom': 3
        },
        'shoreline': {
            'min_lat': -90.0,
            'max_lat': 90.0,
            'min_lon': -180.0,
            'max_lon': 180.0,
            'center': [0.0, 0.0],
            'zoom': 3
        }
    }
    
    def __init__(self, svg_maps_path: Optional[str] = None):
        """
        Initialize map renderer.
        
        Args:
            svg_maps_path: Path to tarkov-dev-svg-maps repository
        """
        self.svg_maps_path = svg_maps_path or "vendor/tarkov-dev-svg-maps"
        
    def _game_to_map_coords(self, x: float, y: float, map_name: str) -> Tuple[float, float]:
        """
        Convert game coordinates to map lat/lon coordinates.
        
        This is a placeholder - actual conversion needs calibration.
        
        Args:
            x: Game X coordinate
            y: Game Y coordinate
            map_name: Map identifier
            
        Returns:
            Tuple of (latitude, longitude)
        """
        bounds = self.MAP_BOUNDS.get(map_name, self.MAP_BOUNDS['customs'])
        
        # Simple linear scaling (needs proper calibration)
        # Game coords typically range from -500 to 500 (approximate)
        game_range = 1000.0
        
        lat_range = bounds['max_lat'] - bounds['min_lat']
        lon_range = bounds['max_lon'] - bounds['min_lon']
        
        lat = bounds['min_lat'] + ((x + 500) / game_range) * lat_range
        lon = bounds['min_lon'] + ((y + 500) / game_range) * lon_range
        
        return (lat, lon)
    
    def create_map(self, map_name: str, level: int = 1) -> folium.Map:
        """
        Create a base Folium map for the specified Tarkov map.
        
        Args:
            map_name: Map name (e.g., 'customs')
            level: Map level/floor (for multi-level maps)
            
        Returns:
            Folium Map object
        """
        bounds = self.MAP_BOUNDS.get(map_name, self.MAP_BOUNDS['customs'])
        
        # Create base map
        m = folium.Map(
            location=bounds['center'],
            zoom_start=bounds['zoom'],
            tiles='OpenStreetMap',
            control_scale=True,
            prefer_canvas=True
        )
        
        # Add fullscreen control
        plugins.Fullscreen(
            position='topright',
            title='Fullscreen',
            title_cancel='Exit fullscreen',
            force_separate_button=True
        ).add_to(m)
        
        # Add mouse position display
        plugins.MousePosition(
            position='bottomleft',
            separator=' | ',
            prefix='Position:',
            num_digits=2
        ).add_to(m)
        
        return m
    
    def add_svg_overlay(self, m: folium.Map, map_name: str, level: int = 1) -> folium.Map:
        """
        Add SVG map overlay from tarkov-dev-svg-maps.
        
        Args:
            m: Folium map object
            map_name: Map name
            level: Map level/floor
            
        Returns:
            Modified map object
        """
        # Path to SVG file
        svg_path = os.path.join(
            self.svg_maps_path,
            f"{map_name}_level{level}.svg"
        )
        
        # Check if SVG exists
        if os.path.exists(svg_path):
            bounds = self.MAP_BOUNDS.get(map_name, self.MAP_BOUNDS['customs'])
            image_bounds = [
                [bounds['min_lat'], bounds['min_lon']],
                [bounds['max_lat'], bounds['max_lon']]
            ]
            
            # Note: Folium doesn't directly support SVG overlays
            # You may need to convert SVG to PNG or use a different approach
            # For now, we'll add a placeholder comment
            # TODO: Integrate actual SVG rendering or convert to raster
            pass
        
        return m
    
    def add_player_marker(
        self, 
        m: folium.Map, 
        position: Dict[str, float], 
        map_name: str
    ) -> folium.Map:
        """
        Add player position marker to the map.
        
        Args:
            m: Folium map object
            position: Position dict with x, y, z, rotation
            map_name: Map name for coordinate conversion
            
        Returns:
            Modified map object
        """
        lat, lon = self._game_to_map_coords(
            position['x'],
            position['y'],
            map_name
        )
        
        # Create custom icon with rotation indicator
        icon_html = f"""
        <div style="transform: rotate({position['rotation']}deg);">
            <i class="fa fa-location-arrow" style="color: red; font-size: 24px;"></i>
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[lat, lon],
            popup=f"You are here<br>Z: {position['z']:.1f}m<br>Facing: {position['rotation']}°",
            tooltip="Your Position",
            icon=folium.DivIcon(html=icon_html)
        ).add_to(m)
        
        # Add circle for visibility
        folium.Circle(
            location=[lat, lon],
            radius=10,
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.3,
            popup="You are here"
        ).add_to(m)
        
        return m
    
    def add_quest_markers(
        self, 
        m: folium.Map, 
        quests: List[Dict[str, Any]], 
        map_name: str
    ) -> folium.Map:
        """
        Add quest objective markers to the map.
        
        Args:
            m: Folium map object
            quests: List of quest data dicts
            map_name: Map name for coordinate conversion
            
        Returns:
            Modified map object
        """
        # Create feature group for quest markers
        quest_group = folium.FeatureGroup(name='Quest Objectives')
        
        for quest in quests:
            # TODO: Extract actual coordinates from quest data
            # For now, use placeholder positions
            # In reality, you'd need coordinate data from the API or map data
            
            quest_name = quest.get('quest_name', 'Unknown Quest')
            obj_desc = quest.get('objective_description', 'Complete objective')
            
            # Placeholder: random position for demonstration
            # Replace with actual quest location coordinates
            lat, lon = 0.0, 0.0
            
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{quest_name}</b><br>{obj_desc}",
                tooltip=quest_name,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(quest_group)
        
        quest_group.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def render_map(
        self,
        map_name: str,
        level: int = 1,
        player_position: Optional[Dict[str, float]] = None,
        quests: Optional[List[Dict[str, Any]]] = None
    ) -> folium.Map:
        """
        Render a complete map with all overlays.
        
        Args:
            map_name: Map name (e.g., 'customs')
            level: Map level/floor
            player_position: Player position dict (optional)
            quests: Quest data list (optional)
            
        Returns:
            Complete Folium map object
        """
        # Create base map
        m = self.create_map(map_name, level)
        
        # Add SVG overlay
        m = self.add_svg_overlay(m, map_name, level)
        
        # Add player marker if position provided
        if player_position:
            m = self.add_player_marker(m, player_position, map_name)
        
        # Add quest markers if provided
        if quests:
            m = self.add_quest_markers(m, quests, map_name)
        
        return m


# Example usage and testing
if __name__ == "__main__":
    print("Testing Map Renderer\n")
    
    renderer = MapRenderer()
    
    # Test player position
    test_position = {
        'x': 100.5,
        'y': 200.3,
        'z': 5.2,
        'rotation': 45
    }
    
    # Test quest data
    test_quests = [
        {
            'quest_name': 'Delivery from the Past',
            'objective_description': 'Place the package in the car trunk',
            'x': 150.0,
            'y': 180.0
        }
    ]
    
    # Render map
    m = renderer.render_map(
        map_name='customs',
        level=1,
        player_position=test_position,
        quests=test_quests
    )
    
    # Save to HTML for testing
    output_path = "test_map.html"
    m.save(output_path)
    print(f"✅ Test map saved to {output_path}")
    print("Open this file in a browser to view the interactive map.")
