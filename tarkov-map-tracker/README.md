# 🎯 Tarkov Interactive Map Tracker

> **Real-time position tracking for Escape from Tarkov PVE**
>
> Made this for myself and my buddies so we can actually know where we are in raids without alt-tabbing every 5 seconds.

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-red.svg)


## ✨ What It Does

- **🎯 Position Tracking** - Reads your screenshot filenames to figure out where you are on the map
- **🗺️ Interactive Maps** - Zoomable maps so you can actually see where stuff is
- **📍 Quest Markers** - Shows where your quest objectives are (super helpful for those annoying fetch quests)
- **🔄 Auto-Refresh** - Updates your position automatically, no clicking needed
- **🎨 Dark UI** - Looks pretty decent and won't blind you at 2 AM
- **⚡ Live Data** - Uses tarkov.dev API for quest info and maps
- **📊 Log Monitoring** - Watches your game logs to detect when you switch maps

## 📋 What You Need

- **Python 3.11+** - [Get it here](https://www.python.org/)
- **Tarkov installed** (obviously)

## 🚀 How to Run This Thing

### The Easy Way

1. **Download/clone this project**

2. **Double-click `start.bat`**
   
   First time: It'll set up everything automatically (takes a minute)
   
   After that: Opens instantly

3. **(Optional) Fix your paths**
   
   If your Tarkov isn't in the default spot, edit `config.yaml`:
   ```yaml
   eft:
     install_path: "C:/Battlestate Games/EFT"
     screenshot_path: "%USERPROFILE%/Documents/Escape from Tarkov/Screenshots"
   ```

### Advanced Installation

If you prefer manual control or want to contribute:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

## 📖 Usage

### Starting the Application

**Easy way:** Just double-click `start.bat`

**Manual way:**
```bash
venv\Scripts\activate.bat
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

### Using the Tracker

1. **Configure Paths**: In the sidebar, set your EFT screenshot and log directories
2. **Select Map**: Choose the map you're currently playing (e.g., Customs)
3. **Update Position**: 
   - **Manual**: Click "Update Position from Screenshot"
   - **Auto**: Enable "Auto-Refresh Position" in sidebar
4. **View Quests**: Toggle quest markers on/off to see objectives
5. **Navigate**: Use mouse to pan and zoom the interactive map

### Screenshot Naming Convention

This app parses screenshot filenames to extract position data. Your screenshots should follow this format:

```
YYYY-MM-DD[HH:MM]_X.XX,Y.YY,Z.ZZ_ROTdeg.png
```

Example: `2025-12-27[15:20]_1234.56,789.01,2.34_45deg.png`

This format is based on the **Tarkov Pilot** tool's screenshot naming convention.

## 🧩 Architecture

### Core Modules

| Module | Description | Source |
|--------|-------------|--------|
| `screenshot_parser.py` | Position extraction from screenshots | Ported from Tarkov Pilot (PowerShell) |
| `log_monitor.py` | EFT log file event detection | Ported from TarkovMonitor (C#) |
| `tarkov_api.py` | GraphQL API client | Based on tarkov-api schema |
| `map_renderer.py` | Interactive map rendering | Using tarkov-dev-svg-maps |
| `app.py` | Main Streamlit application | Original |

### Repository Integration

This project integrates multiple repositories from [the-hideout](https://github.com/the-hideout) organization:

- **TarkovMonitor** (160⭐): Log parsing patterns
- **tarkov-api** (177⭐): GraphQL API schema
- **tarkov-dev-svg-maps**: SVG map assets
- **tarkov-dev** (188⭐): UI reference

## 🛠️ Development

### Project Structure

```
tarkov-map-tracker/
├── app.py                    # Main Streamlit app
├── screenshot_parser.py      # Screenshot parsing (Tarkov Pilot port)
├── log_monitor.py           # Log monitoring (TarkovMonitor port)
├── tarkov_api.py            # GraphQL API client
├── map_renderer.py          # Map rendering with Folium
├── config.yaml              # User configuration
├── requirements.txt         # Python dependencies
├── setup.bat                # Windows setup script
├── .gitmodules             # Git submodule configuration
├── vendor/                 # Git submodules (not tracked)
│   ├── TarkovMonitor/
│   ├── tarkov-api/
│   ├── tarkov-dev-svg-maps/
│   └── tarkov-dev/
└── README.md               # This file
```

### Testing Individual Modules

Each core module can be run standalone for testing:

```bash
# Test screenshot parser
python screenshot_parser.py "C:/path/to/screenshots"

# Test log monitor
python log_monitor.py "%APPDATA%/../LocalLow/Battlestate Games/EscapeFromTarkov"

# Test API client
python tarkov_api.py
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No valid position screenshot found"
- **Solution**: Ensure your screenshots follow the expected naming format. Take a new screenshot in-game.

**Issue**: "Could not load maps from API"
- **Solution**: Check your internet connection. The app requires access to api.tarkov.dev.

**Issue**: "Error finding log file"
- **Solution**: Verify the log path in config.yaml matches your EFT installation.

**Issue**: Submodules are empty
- **Solution**: Run `git submodule update --init --recursive`

## 📄 License

This project is licensed under the **GPL-3.0 License** to comply with the licenses of integrated repositories.

### Attribution

This project uses code and data from:
- [the-hideout/TarkovMonitor](https://github.com/the-hideout/TarkovMonitor) (GPL-3.0)
- [the-hideout/tarkov-api](https://github.com/the-hideout/tarkov-api) (MIT)
- [the-hideout/tarkov-dev-svg-maps](https://github.com/the-hideout/tarkov-dev-svg-maps) (MIT)
- [the-hideout/tarkov-dev](https://github.com/the-hideout/tarkov-dev) (MIT)

## ⚠️ Disclaimer

This isn't official or anything - just a fan project. EFT belongs to Battlestate Games.

It's totally safe though - just reads screenshots and log files, doesn't touch the game at all.

## 🤝 Contributing

If you wanna improve something or fix a bug, go for it! PRs are welcome.

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Consult the [tarkov.dev](https://tarkov.dev) community

## 🙏 Acknowledgments

- **the-hideout** team for their excellent open-source tools and APIs
- **tarkov.dev** community for map data and documentation
- **Tarkov Pilot** for the screenshot parsing concept
- All contributors to the Tarkov development ecosystem

---

## 👤 About This Thing

Made by **Shadesz** with some help from AI because why not.

Originally whipped this up for myself and my friends to use in PVE mode. We kept getting lost and I was tired of alt-tabbing to check maps every 30 seconds, so... here we are.

Feel free to use it if you want! It works pretty well for us.

*Good luck out there, try not to die immediately* ⚡
