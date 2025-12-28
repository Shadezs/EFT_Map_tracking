"""
Map Renderer
Renders interactive Tarkov maps using SVG maps and configuration from tarkov.dev.
"""

import os
import json
import requests
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import xml.etree.ElementTree as ET


class MapRenderer:
    """Renders interactive maps using SVG files and data from tarkov.dev."""
    
    # URLs for data and maps
    MAPS_JSON_URL = "https://raw.githubusercontent.com/the-hideout/tarkov-dev/main/src/data/maps.json"
    SVG_BASE_URL = "https://raw.githubusercontent.com/the-hideout/tarkov-dev-svg-maps/main"
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize map renderer.
        
        Args:
            cache_dir: Directory to cache downloaded files
        """
        self.cache_dir = Path(cache_dir or "map_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.maps_config = self._load_maps_config()
    
    def _load_maps_config(self) -> List[Dict[str, Any]]:
        """Load maps configuration from GitHub or cache."""
        local_path = self.cache_dir / "maps.json"
        
        # Try local cache first
        if local_path.exists():
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Download from GitHub
        try:
            response = requests.get(self.MAPS_JSON_URL, timeout=10)
            if response.status_code == 200:
                config = response.json()
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f)
                return config
        except Exception as e:
            print(f"Error loading maps config: {e}")
        
        return []

    def _get_map_config(self, normalized_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific map."""
        for map_entry in self.maps_config:
            if map_entry.get('normalizedName') == normalized_name:
                # Use the 'interactive' projection map if available
                for m in map_entry.get('maps', []):
                    if m.get('projection') == 'interactive':
                        return m
                # Fallback to first map
                if map_entry.get('maps'):
                    return map_entry['maps'][0]
        return None

    def _get_svg_content(self, map_config: Dict[str, Any]) -> Optional[str]:
        """Download or load SVG content."""
        svg_url = map_config.get('svgPath')
        if not svg_url:
            # Construct from name if not provided (fallback)
            svg_filename = f"{map_config.get('key','').capitalize()}.svg"
            svg_url = f"{self.SVG_BASE_URL}/{svg_filename}"
        
        filename = Path(svg_url).name
        local_path = self.cache_dir / filename
        
        if local_path.exists():
            with open(local_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        try:
            print(f"Downloading SVG from: {svg_url}")
            response = requests.get(svg_url, timeout=10)
            if response.status_code == 200:
                svg_content = response.text
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                return svg_content
            else:
                print(f"Failed to download SVG: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error downloading SVG: {e}")
            
        return None

    def _calculate_svg_coords(
        self, 
        game_x: float, 
        game_y: float, 
        map_config: Dict[str, Any],
        width: float,
        height: float
    ) -> Tuple[float, float]:
        """
        Convert game coordinates to SVG coordinates based on bounds and rotation.
        """
        bounds = map_config.get('bounds')
        rotation = map_config.get('coordinateRotation', 0)
        
        if not bounds or len(bounds) < 2:
            # Fallback to rough estimation
            return (game_x + 500), (500 - game_y)
            
        # Bounds format: [[minX, maxY], [maxX, minY]]
        min_x = bounds[1][0] if bounds[0][0] > bounds[1][0] else bounds[0][0]
        max_x = bounds[0][0] if bounds[0][0] > bounds[1][0] else bounds[1][0]
        min_y = bounds[1][1] if bounds[0][1] > bounds[1][1] else bounds[0][1]
        max_y = bounds[0][1] if bounds[0][1] > bounds[1][1] else bounds[1][1]
        
        # Apply rotation to game coordinates if needed
        # (This is a simplified version, real rotation might be more complex)
        rad = math.radians(rotation)
        rot_x = game_x * math.cos(rad) - game_y * math.sin(rad)
        rot_y = game_x * math.sin(rad) + game_y * math.cos(rad)
        
        # Scale to map dimensions
        # This is where we'd need the SVG viewBox actually
        # But for now let's use the percentile within bounds
        range_x = max_x - min_x if max_x != min_x else 1000
        range_y = max_y - min_y if max_y != min_y else 1000
        
        perc_x = (game_x - min_x) / range_x
        perc_y = (max_y - game_y) / range_y # Y is usually inverted in SVG
        
        return perc_x * 100, perc_y * 100 # Returns as percentage for flexible SVG usage

    def render_map(
        self,
        map_name: str,
        level: int = 1,
        player_position: Optional[Dict[str, float]] = None,
        quests: Optional[List[Dict[str, Any]]] = None,
        width: int = 900,
        height: int = 600
    ) -> str:
        """Render map as HTML using Leaflet.js."""
        map_config = self._get_map_config(map_name)
        
        if not map_config:
            return f"<div style='color:red; background:#1a1a1a; padding:20px;'>Map config not found for {map_name}</div>"
            
        # Prioritize the tarkov-dev-svg-maps repo URL
        map_key = map_config.get('key', '')
        # Special case for streets because the key is 'streets-of-tarkov' but filename is 'StreetsOfTarkov.svg'
        # We can use our MAP_FILES mapping logic or just construct it
        svg_filename = f"{map_key.replace('-', ' ').title().replace(' ', '')}.svg"
        if map_key == 'streets-of-tarkov':
            svg_filename = "StreetsOfTarkov.svg"
            
        svg_url = f"{self.SVG_BASE_URL}/{svg_filename}"
        
        # Leaflet Configuration
        bounds = map_config.get('bounds', [[0, 0], [1000, 1000]])
        # bounds are [[minX, maxY], [maxX, minY]] or similar
        # For Leaflet L.ImageOverlay, we need [[minY, minX], [maxY, maxX]] usually, 
        # but tarkov.dev uses CRS.Simple with a custom transformation.
        
        transform = map_config.get('transform', [1, 0, 1, 0])
        # transform is [a, b, c, d] for L.Transformation(a, b, c, d)
        
        # Prepare markers for JS
        js_markers = []
        if player_position:
            js_markers.append({
                'lat': player_position['y'],
                'lng': player_position['x'],
                'title': 'YOU',
                'color': '#ff4141',
                'rotation': player_position.get('rotation', 0),
                'type': 'player'
            })
            
        if quests:
            for i, quest in enumerate(quests):
                if 'x' in quest and 'y' in quest:
                    js_markers.append({
                        'lat': quest['y'],
                        'lng': quest['x'],
                        'title': quest.get('quest_name', f'Quest {i+1}'),
                        'color': '#0088ff',
                        'type': 'quest'
                    })

        # Leaflet implementation
        html = f"""
        <div id="map-host" style="width:{width}px; height:{height}px; background:#0f1112; border:1px solid #2d3336; border-radius:8px; overflow:hidden;">
            <div id="leaflet-map" style="width:100%; height:100%;"></div>
        </div>
        
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        
        <script>
            (function() {{
                // Initialize Map
                const map = L.map('leaflet-map', {{
                    crs: L.CRS.Simple,
                    attributionControl: false,
                    zoomControl: true,
                    minZoom: {map_config.get('minZoom', 1)},
                    maxZoom: {map_config.get('maxZoom', 5)}
                }});

                // Set up Transformation (a, b, c, d)
                // L.Transformation transforms coordinates: x' = a*x + b, y' = c*y + d
                const t = {transform};
                L.CRS.Simple.transformation = new L.Transformation(t[0], t[1], t[2], t[3]);

                // SVG Overlay
                const bounds = {bounds};
                
                // Calculate correct min/max to support various bounds formats
                const x1 = bounds[0][0];
                const y1 = bounds[0][1];
                const x2 = bounds[1][0];
                const y2 = bounds[1][1];
                
                const minX = Math.min(x1, x2);
                const maxX = Math.max(x1, x2);
                const minY = Math.min(y1, y2);
                const maxY = Math.max(y1, y2);

                // Leaflet Simple CRS uses [y, x] order
                const southWest = L.latLng(minY, minX);
                const northEast = L.latLng(maxY, maxX);
                const mapBounds = L.latLngBounds(southWest, northEast);

                const svgLayer = L.imageOverlay('{svg_url}', mapBounds);
                svgLayer.addTo(map);

                // Fit map to bounds
                map.fitBounds(mapBounds);

                // Markers
                const markers = {json.dumps(js_markers)};
                markers.forEach(m => {{
                    let icon;
                    if (m.type === 'player') {{
                        icon = L.divIcon({{
                            className: 'player-marker',
                            html: `<div style="transform: rotate(${{m.rotation}}deg); color: ${{m.color}}; font-size: 24px; text-shadow: 0 0 3px black;">▲</div>`,
                            iconSize: [30, 30],
                            iconAnchor: [15, 15]
                        }});
                    }} else {{
                        icon = L.divIcon({{
                            className: 'quest-marker',
                            html: `<div style="background: ${{m.color}}; border: 2px solid white; border-radius: 50%; width: 14px; height: 14px; box-shadow: 0 0 5px black;"></div>`,
                            iconSize: [20, 20],
                            iconAnchor: [10, 10]
                        }});
                    }}

                    L.marker([m.lat, m.lng], {{ icon: icon }})
                        .addTo(map)
                        .bindPopup(`<b>${{m.title}}</b>`);
                }});

                // Coordinate Logger for debugging
                map.on('click', function(e) {{
                    console.log("Clicked at: " + e.latlng.lng.toFixed(2) + ", " + e.latlng.lat.toFixed(2));
                }});
            }})();
        </script>
        
        <style>
            .player-marker, .quest-marker {{
                display: flex;
                align-items: center;
                justify-content: center;
                pointer-events: auto !important;
            }}
            .leaflet-container {{
                background: #0f1112 !important;
            }}
            .leaflet-popup-content-wrapper, .leaflet-popup-tip {{
                background: #1a1c1d;
                color: #e3e3e3;
                border: 1px solid #2d3336;
            }}
        </style>
        """
        return html
