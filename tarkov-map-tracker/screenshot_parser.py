"""
Screenshot Parser - Tarkov Pilot PowerShell Port
Parses EFT screenshot filenames to extract player position data.

Original PowerShell logic from Tarkov Pilot ported to Python.
Expected filename format: YYYY-MM-DD[HH:MM]_X.XX,Y.YY,Z.ZZ_ROTdeg.png
Example: 2025-12-27[15:20]_1234.56,789.01,2.34_45deg.png
"""

import re
import glob
import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class ScreenshotParser:
    """Parses Tarkov screenshot filenames to extract position data."""
    
    # Regex pattern to match position data in filename
    # Matches: _X.XX,Y.YY,Z.ZZ_ROTdeg.png
    POSITION_PATTERN = re.compile(
        r"_(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*)_(\d+)deg\.png$",
        re.IGNORECASE
    )
    
    def __init__(self, screenshot_path: str):
        """
        Initialize the screenshot parser.
        
        Args:
            screenshot_path: Directory path containing EFT screenshots
        """
        self.screenshot_path = os.path.expandvars(screenshot_path)
        
    def get_latest_screenshot(self) -> Optional[str]:
        """
        Find the most recently modified screenshot file.
        
        Returns:
            Path to the latest screenshot, or None if no screenshots found
        """
        try:
            screenshots = glob.glob(os.path.join(self.screenshot_path, "*.png"))
            if not screenshots:
                return None
            return max(screenshots, key=os.path.getmtime)
        except (OSError, ValueError) as e:
            print(f"Error finding screenshots: {e}")
            return None
    
    def parse_filename(self, filename: str) -> Optional[Dict[str, float]]:
        """
        Parse position data from a screenshot filename.
        
        Args:
            filename: Full path or just filename of the screenshot
            
        Returns:
            Dict with keys: x, y, z, rotation, timestamp
            Returns None if filename doesn't match expected pattern
        """
        basename = Path(filename).name
        match = self.POSITION_PATTERN.search(basename)
        
        if not match:
            return None
        
        try:
            position_data = {
                'x': float(match.group(1)),
                'y': float(match.group(2)),
                'z': float(match.group(3)),
                'rotation': int(match.group(4)),
                'filename': basename,
                'timestamp': os.path.getmtime(filename) if os.path.exists(filename) else None
            }
            return position_data
        except (ValueError, IndexError) as e:
            print(f"Error parsing position from {basename}: {e}")
            return None
    
    def get_latest_position(self) -> Optional[Dict[str, float]]:
        """
        Get position data from the most recent screenshot.
        
        This is the main function - equivalent to Tarkov Pilot's PowerShell logic.
        
        Returns:
            Dict with position data, or None if no valid screenshot found
        """
        latest = self.get_latest_screenshot()
        if not latest:
            return None
        return self.parse_filename(latest)
    
    def watch_for_updates(self, callback, interval: float = 1.0):
        """
        Continuously monitor for new screenshots and call callback with position data.
        
        Args:
            callback: Function to call with position data when new screenshot detected
            interval: How often to check for updates (seconds)
        """
        import time
        last_file = None
        last_mtime = 0
        
        while True:
            try:
                latest = self.get_latest_screenshot()
                if latest and latest != last_file:
                    mtime = os.path.getmtime(latest)
                    if mtime > last_mtime:
                        position = self.parse_filename(latest)
                        if position:
                            callback(position)
                        last_file = latest
                        last_mtime = mtime
            except Exception as e:
                print(f"Error in watch loop: {e}")
            
            time.sleep(interval)


def get_latest_position(screenshot_path: str) -> Optional[Dict[str, float]]:
    """
    Convenience function to get latest position without creating a parser instance.
    
    This matches the function signature shown in the requirements.
    
    Args:
        screenshot_path: Directory containing EFT screenshots
        
    Returns:
        Dict with x, y, z, rotation, or None if no valid screenshot
    """
    parser = ScreenshotParser(screenshot_path)
    return parser.get_latest_position()


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python screenshot_parser.py <screenshot_directory>")
        print("\nExample:")
        print("  python screenshot_parser.py 'C:/Users/YourName/Documents/Escape from Tarkov/Screenshots'")
        sys.exit(1)
    
    path = sys.argv[1]
    print(f"Monitoring screenshots in: {path}\n")
    
    parser = ScreenshotParser(path)
    position = parser.get_latest_position()
    
    if position:
        print("Latest position found:")
        print(f"  X: {position['x']}")
        print(f"  Y: {position['y']}")
        print(f"  Z: {position['z']}")
        print(f"  Rotation: {position['rotation']}°")
        print(f"  File: {position['filename']}")
    else:
        print("No valid position screenshots found.")
        print("\nExpected filename format:")
        print("  YYYY-MM-DD[HH:MM]_X.XX,Y.YY,Z.ZZ_ROTdeg.png")
        print("  Example: 2025-12-27[15:20]_1234.56,789.01,2.34_45deg.png")
