"""
Tarkov API Integration
GraphQL client for the-hideout/tarkov-api (tarkov.dev API)

Fetches quest data, map information, and other game data.
"""

import time
import requests
from typing import Dict, List, Optional, Any
from functools import lru_cache


class TarkovAPI:
    """Client for tarkov.dev GraphQL API."""
    
    API_URL = "https://api.tarkov.dev/graphql"
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the API client.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 5 minutes)
        """
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[float, Any]] = {}
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key in self._cache:
            timestamp, value = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return value
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Store value in cache with timestamp."""
        self._cache[key] = (time.time(), value)
    
    def _query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Query variables dict
            
        Returns:
            Response data dict or None on error
        """
        try:
            response = requests.post(
                self.API_URL,
                json={'query': query, 'variables': variables or {}},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if 'errors' in result:
                print(f"GraphQL errors: {result['errors']}")
                return None
            
            return result.get('data')
        except Exception as e:
            print(f"API query error: {e}")
            return None
    
    def get_maps(self) -> List[Dict[str, Any]]:
        """
        Fetch all available maps.
        
        Returns:
            List of map objects with id, name, and other properties
        """
        cache_key = "maps"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        query = """
        query {
            maps {
                id
                name
                normalizedName
                wiki
                description
                enemies
                raidDuration
            }
        }
        """
        
        data = self._query(query)
        if data and 'maps' in data:
            self._set_cache(cache_key, data['maps'])
            return data['maps']
        return []
    
    def get_quests(self, map_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch quest data, optionally filtered by map.
        
        Args:
            map_name: Filter quests by map (e.g., 'customs')
            
        Returns:
            List of quest objects with objectives and locations
        """
        cache_key = f"quests_{map_name or 'all'}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        query = """
        query {
            tasks {
                id
                name
                normalizedName
                trader {
                    name
                }
                map {
                    name
                    normalizedName
                }
                experience
                objectives {
                    id
                    type
                    description
                    optional
                    maps {
                        name
                        normalizedName
                    }
                    ...on TaskObjectiveBasic {
                        zones {
                            map { normalizedName }
                            position { x y z }
                        }
                    }
                    ...on TaskObjectiveItem {
                        zones {
                            map { normalizedName }
                            position { x y z }
                        }
                    }
                    ...on TaskObjectiveMark {
                        zones {
                            map { normalizedName }
                            position { x y z }
                        }
                    }
                    ...on TaskObjectiveQuestItem {
                        zones {
                            map { normalizedName }
                            position { x y z }
                        }
                        possibleLocations {
                            map { normalizedName }
                            positions { x y z }
                        }
                    }
                }
            }
        }
        """
        
        data = self._query(query)
        if not data or 'tasks' not in data:
            return []
        
        quests = data['tasks']
        
        # Filter by map if specified
        if map_name:
            map_name_lower = map_name.lower()
            quests = [
                q for q in quests
                if q.get('map') and q['map'].get('normalizedName', '').lower() == map_name_lower
            ]
        
        self._set_cache(cache_key, quests)
        return quests
    
    def get_map_data(self, map_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed data for a specific map.
        
        Args:
            map_name: Normalized map name (e.g., 'customs')
            
        Returns:
            Map data dict or None if not found
        """
        maps = self.get_maps()
        for m in maps:
            if m.get('normalizedName', '').lower() == map_name.lower():
                return m
        return None
    
    def get_items(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch item data, optionally filtered by category.
        
        Args:
            category: Filter items by category name
            
        Returns:
            List of item objects
        """
        cache_key = f"items_{category or 'all'}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        query = """
        query {
            items {
                id
                name
                shortName
                basePrice
                width
                height
                iconLink
                wikiLink
                types
            }
        }
        """
        
        data = self._query(query)
        if not data or 'items' not in data:
            return []
        
        items = data['items']
        
        # Filter by category if specified
        if category:
            category_lower = category.lower()
            items = [
                i for i in items
                if category_lower in [t.lower() for t in i.get('types', [])]
            ]
        
        self._set_cache(cache_key, items)
        return items
    
    def get_quest_objectives_with_locations(self, map_name: str) -> List[Dict[str, Any]]:
        """
        Get quest objectives for a map with their locations.
        This is useful for plotting quest markers on the map.
        
        Args:
            map_name: Map name (e.g., 'customs')
            
        Returns:
            List of objectives with location data
        """
        quests = self.get_quests(map_name)
        objectives_with_locations = []
        
        for quest in quests:
            for obj in quest.get('objectives', []):
                coords = []
                
                # Extract coordinates from zones
                for zone in obj.get('zones', []) or []:
                    zone_map = zone.get('map', {}).get('normalizedName', '').lower()
                    if zone_map == map_name.lower():
                        pos = zone.get('position')
                        if pos:
                            coords.append({'x': pos['x'], 'y': pos['y']})
                            
                # Extract coordinates from possibleLocations
                for loc in obj.get('possibleLocations', []) or []:
                    loc_map = loc.get('map', {}).get('normalizedName', '').lower()
                    if loc_map == map_name.lower():
                        for pos in loc.get('positions', []) or []:
                            coords.append({'x': pos['x'], 'y': pos['y']})
                
                # If we have coordinates, add them
                for coord in coords:
                    objectives_with_locations.append({
                        'quest_id': quest['id'],
                        'quest_name': quest['name'],
                        'objective_id': obj['id'],
                        'objective_description': obj['description'],
                        'objective_type': obj['type'],
                        'optional': obj.get('optional', False),
                        'trader': quest.get('trader', {}).get('name', 'Unknown'),
                        'x': coord['x'],
                        'y': coord['y']
                    })
        
        return objectives_with_locations


def get_active_quests(map_name: str = "customs") -> List[Dict[str, Any]]:
    """
    Convenience function to get active quests for a map.
    
    Args:
        map_name: Map name to get quests for
        
    Returns:
        List of quest data dicts
    """
    api = TarkovAPI()
    return api.get_quests(map_name)


# Example usage and testing
if __name__ == "__main__":
    print("Testing Tarkov API Integration\n")
    
    api = TarkovAPI()
    
    # Test maps
    print("=== Available Maps ===")
    maps = api.get_maps()
    for m in maps[:5]:  # Show first 5
        print(f"  {m['name']} ({m['normalizedName']})")
    print(f"  ... and {len(maps) - 5} more\n")
    
    # Test quests for Customs
    print("=== Customs Quests ===")
    customs_quests = api.get_quests("customs")
    print(f"Found {len(customs_quests)} quests for Customs")
    for q in customs_quests[:3]:  # Show first 3
        trader = q.get('trader', {}).get('name', 'Unknown')
        print(f"  {q['name']} (Trader: {trader})")
        print(f"    Objectives: {len(q.get('objectives', []))}")
    
    # Test quest objectives with locations
    print("\n=== Quest Objectives for Customs ===")
    objectives = api.get_quest_objectives_with_locations("customs")
    print(f"Found {len(objectives)} objectives with location data")
    for obj in objectives[:3]:  # Show first 3
        print(f"  {obj['quest_name']}")
        print(f"    {obj['objective_description']}")
        print(f"    Type: {obj['objective_type']}, Trader: {obj['trader']}")
    
    print("\n✅ API integration test complete!")
