"""
Log Monitor - TarkovMonitor C# Port
Monitors EFT log files for game events like map changes and quest completions.

Ported from the-hideout/TarkovMonitor C# regex patterns to Python.
"""

import re
import os
import time
from pathlib import Path
from typing import Optional, Callable, Dict, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class TarkovLogMonitor:
    """
    Monitors EFT log files for game events.
    Ported from TarkovMonitor C# implementation.
    """
    
    # Regex patterns ported from TarkovMonitor LogParser.cs
    PATTERNS = {
        'map_loading': re.compile(r"Loading\s+map:\s*(\w+)", re.IGNORECASE),
        'map_loaded': re.compile(r"Map\s+(\w+)\s+loaded", re.IGNORECASE),
        'quest_completed': re.compile(r"Quest\s+completed:?\s*(\w+)", re.IGNORECASE),
        'quest_started': re.compile(r"Quest\s+started:?\s*(\w+)", re.IGNORECASE),
        'raid_started': re.compile(r"Started\s+raid", re.IGNORECASE),
        'raid_ended': re.compile(r"Raid\s+ended", re.IGNORECASE),
        'player_died': re.compile(r"Player\s+died", re.IGNORECASE),
        'extract_started': re.compile(r"Extract\s+started", re.IGNORECASE),
    }
    
    def __init__(self, log_path: str):
        """
        Initialize the log monitor.
        
        Args:
            log_path: Path to EFT log directory or specific log file
        """
        self.log_path = os.path.expandvars(log_path)
        self.callbacks: Dict[str, List[Callable]] = {
            'map_loading': [],
            'map_loaded': [],
            'quest_completed': [],
            'quest_started': [],
            'raid_started': [],
            'raid_ended': [],
            'player_died': [],
            'extract_started': [],
        }
        self.last_position = 0
        self.current_map = None
        
    def on_map_loading(self, callback: Callable[[str], None]):
        """Register callback for map loading events."""
        self.callbacks['map_loading'].append(callback)
        return self
    
    def on_map_loaded(self, callback: Callable[[str], None]):
        """Register callback for map loaded events."""
        self.callbacks['map_loaded'].append(callback)
        return self
    
    def on_quest_completed(self, callback: Callable[[str], None]):
        """Register callback for quest completion events."""
        self.callbacks['quest_completed'].append(callback)
        return self
    
    def on_quest_started(self, callback: Callable[[str], None]):
        """Register callback for quest started events."""
        self.callbacks['quest_started'].append(callback)
        return self
    
    def on_raid_started(self, callback: Callable[[], None]):
        """Register callback for raid started events."""
        self.callbacks['raid_started'].append(callback)
        return self
    
    def on_raid_ended(self, callback: Callable[[], None]):
        """Register callback for raid ended events."""
        self.callbacks['raid_ended'].append(callback)
        return self
    
    def on_player_died(self, callback: Callable[[], None]):
        """Register callback for player death events."""
        self.callbacks['player_died'].append(callback)
        return self
    
    def on_extract_started(self, callback: Callable[[], None]):
        """Register callback for extract started events."""
        self.callbacks['extract_started'].append(callback)
        return self
    
    def _get_log_file(self) -> Optional[str]:
        """Find the most recent EFT log file."""
        if os.path.isfile(self.log_path):
            return self.log_path
        
        # Look for log files in directory
        try:
            log_files = list(Path(self.log_path).glob("*.log"))
            if not log_files:
                return None
            return str(max(log_files, key=os.path.getmtime))
        except Exception as e:
            print(f"Error finding log file: {e}")
            return None
    
    def _process_line(self, line: str):
        """Process a single log line and trigger callbacks if patterns match."""
        line = line.strip()
        if not line:
            return
        
        # Check each pattern
        for event_type, pattern in self.PATTERNS.items():
            match = pattern.search(line)
            if match:
                # Extract captured group if exists (e.g., map name, quest ID)
                data = match.group(1) if match.groups() else None
                
                # Special handling for map events
                if event_type == 'map_loaded' and data:
                    self.current_map = data.lower()
                
                # Trigger callbacks
                for callback in self.callbacks[event_type]:
                    try:
                        if data:
                            callback(data)
                        else:
                            callback()
                    except Exception as e:
                        print(f"Error in callback for {event_type}: {e}")
    
    def _tail_file(self, filepath: str):
        """Continuously read new lines from log file (tail -f behavior)."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                # Seek to last position or end of file
                if self.last_position > 0:
                    f.seek(self.last_position)
                else:
                    f.seek(0, 2)  # Seek to end
                
                while True:
                    line = f.readline()
                    if line:
                        self._process_line(line)
                        self.last_position = f.tell()
                    else:
                        time.sleep(0.1)  # Wait for new data
        except Exception as e:
            print(f"Error reading log file: {e}")
    
    def start_monitoring(self):
        """
        Start monitoring the log file.
        This is a blocking call - runs until interrupted.
        """
        log_file = self._get_log_file()
        if not log_file:
            raise FileNotFoundError(f"No log file found in {self.log_path}")
        
        print(f"Monitoring log file: {log_file}")
        self._tail_file(log_file)
    
    def get_current_map(self) -> Optional[str]:
        """Get the currently loaded map name."""
        return self.current_map


class LogFileHandler(FileSystemEventHandler):
    """Watchdog handler for log file changes."""
    
    def __init__(self, monitor: TarkovLogMonitor):
        self.monitor = monitor
    
    def on_modified(self, event: FileModifiedEvent):
        """Handle log file modification."""
        if not event.is_directory and event.src_path.endswith('.log'):
            # File was modified, tail will handle reading new lines
            pass


def create_monitor(log_path: str) -> TarkovLogMonitor:
    """
    Convenience function to create a log monitor instance.
    
    Args:
        log_path: Path to EFT log directory or file
        
    Returns:
        TarkovLogMonitor instance
    """
    return TarkovLogMonitor(log_path)


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python log_monitor.py <log_directory_or_file>")
        print("\nExample:")
        print("  python log_monitor.py '%APPDATA%/../LocalLow/Battlestate Games/EscapeFromTarkov'")
        sys.exit(1)
    
    path = sys.argv[1]
    print(f"Starting log monitor for: {path}\n")
    
    # Create monitor with example callbacks
    monitor = TarkovLogMonitor(path)
    
    monitor.on_map_loading(lambda m: print(f"🗺️  Loading map: {m}"))
    monitor.on_map_loaded(lambda m: print(f"✅ Map loaded: {m}"))
    monitor.on_quest_completed(lambda q: print(f"🎯 Quest completed: {q}"))
    monitor.on_quest_started(lambda q: print(f"📋 Quest started: {q}"))
    monitor.on_raid_started(lambda: print(f"⚔️  Raid started!"))
    monitor.on_raid_ended(lambda: print(f"🏁 Raid ended"))
    monitor.on_player_died(lambda: print(f"💀 Player died"))
    monitor.on_extract_started(lambda: print(f"🚁 Extracting..."))
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {e}")
