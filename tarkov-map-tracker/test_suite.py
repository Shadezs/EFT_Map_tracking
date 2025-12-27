"""
Test Suite for Tarkov Map Tracker
Comprehensive tests for all modules
"""

import os
import sys
import tempfile
from pathlib import Path

def test_screenshot_parser():
    """Test screenshot filename parsing."""
    print("\n" + "="*50)
    print("TEST: Screenshot Parser")
    print("="*50)
    
    from screenshot_parser import ScreenshotParser
    
    # Create temp directory with test screenshot
    tmpdir = tempfile.mkdtemp()
    testfile = os.path.join(tmpdir, '2025-12-27[15:20]_1234.56,789.01,2.34_45deg.png')
    Path(testfile).touch()
    
    # Test parsing
    parser = ScreenshotParser(tmpdir)
    pos = parser.get_latest_position()
    
    if pos and pos['x'] == 1234.56 and pos['y'] == 789.01 and pos['rotation'] == 45:
        print("✅ PASSED - Screenshot parsing works correctly")
        print(f"   Position: X={pos['x']}, Y={pos['y']}, Z={pos['z']}, Rotation={pos['rotation']}°")
        return True
    else:
        print("❌ FAILED - Incorrect parsing")
        return False

def test_api_integration():
    """Test Tarkov API connectivity."""
    print("\n" + "="*50)
    print("TEST: API Integration")
    print("="*50)
    
    from tarkov_api import TarkovAPI
    
    api = TarkovAPI()
    
    # Test maps retrieval
    maps = api.get_maps()
    print(f"✅ Retrieved {len(maps)} maps from API")
    
    # Test quests retrieval
    quests = api.get_quests("customs")
    print(f"✅ Retrieved {len(quests)} Customs quests")
    
    # Test quest objectives
    objectives = api.get_quest_objectives_with_locations("customs")
    print(f"✅ Retrieved {len(objectives)} quest objectives with locations")
    
    return len(maps) > 0 and len(quests) > 0

def test_map_renderer():
    """Test map rendering."""
    print("\n" + "="*50)
    print("TEST: Map Renderer")
    print("="*50)
    
    from map_renderer import MapRenderer
    
    renderer = MapRenderer()
    test_pos = {'x': 100.5, 'y': 200.3, 'z': 5.2, 'rotation': 45}
    
    try:
        m = renderer.render_map('customs', level=1, player_position=test_pos)
        m.save('test_map.html')
        print("✅ PASSED - Map rendered successfully")
        print("   Output: test_map.html")
        return True
    except Exception as e:
        print(f"⚠️  WARNING - Map rendering had issues: {e}")
        return False

def test_log_monitor():
    """Test log monitor setup."""
    print("\n" + "="*50)
    print("TEST: Log Monitor")
    print("="*50)
    
    from log_monitor import TarkovLogMonitor
    
    try:
        # Just test that we can create a monitor instance
        tmpdir = tempfile.mkdtemp()
        monitor = TarkovLogMonitor(tmpdir)
        print("✅ PASSED - Log monitor initialized")
        return True
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def test_module_imports():
    """Test that all modules can be imported."""
    print("\n" + "="*50)
    print("TEST: Module Imports")
    print("="*50)
    
    modules = ['screenshot_parser', 'log_monitor', 'tarkov_api', 'map_renderer']
    all_passed = True
    
    for mod in modules:
        try:
            __import__(mod)
            print(f"✅ {mod}")
        except Exception as e:
            print(f"❌ {mod}: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("\n" + "🧪 TARKOV MAP TRACKER TEST SUITE 🧪".center(50))
    print("="*50)
    
    results = {}
    
    # Run tests
    results['Module Imports'] = test_module_imports()
    results['Screenshot Parser'] = test_screenshot_parser()
    results['API Integration'] = test_api_integration()
    results['Map Renderer'] = test_map_renderer()
    results['Log Monitor'] = test_log_monitor()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test}")
    
    print("="*50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Application is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
    
    sys.exit(0 if passed == total else 1)
