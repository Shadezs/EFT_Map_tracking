# Tarkov Interactive Map Tracker

A Python-based desktop application for Escape from Tarkov that provides real-time position tracking and interactive maps, replicating the functionality of tarkov-market.com/maps with enhanced live tracking capabilities.

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-red.svg)

## 🌟 Features

- **Real-Time Position Tracking**: Automatically parses screenshot filenames to extract and display your current position on the map
- **Interactive Maps**: Multi-level, zoomable maps powered by Folium
- **Quest Overlays**: Display active quest objectives directly on the map
- **Live Monitoring**: Auto-refresh position updates while playing
- **Dark Tactical UI**: Clean, military-themed interface built with Streamlit
- **GraphQL API Integration**: Leverages tarkov.dev API for up-to-date quest and map data
- **Log File Monitoring**: Detects map changes and game events from EFT logs

## 📋 Prerequisites

- **Python 3.11 or later**
- **Git** (for cloning submodules)
- **Escape from Tarkov** installed
- **Internet connection** (for API queries)

## 🚀 Installation

### Windows

1. **Clone or download this repository**
   ```bash
   git clone <your-repo-url>
   cd tarkov-map-tracker
   ```

2. **Run the setup script**
   ```bash
   setup.bat
   ```
   
   This will:
   - Initialize git repository
   - Clone all required the-hideout submodules
   - Create a Python virtual environment
   - Install all dependencies

3. **Configure paths**
   
   Edit `config.yaml` with your EFT installation paths:
   ```yaml
   eft:
     install_path: "C:/Battlestate Games/EFT"
     log_path: "%APPDATA%/../LocalLow/Battlestate Games/EscapeFromTarkov"
     screenshot_path: "%USERPROFILE%/Documents/Escape from Tarkov/Screenshots"
   ```

### Manual Installation

If the setup script doesn't work, follow these steps:

```bash
# 1. Initialize git and add submodules
git init
git submodule add https://github.com/the-hideout/TarkovMonitor.git vendor/TarkovMonitor
git submodule add https://github.com/the-hideout/tarkov-api.git vendor/tarkov-api
git submodule add https://github.com/the-hideout/tarkov-dev-svg-maps.git vendor/tarkov-dev-svg-maps
git submodule add https://github.com/the-hideout/tarkov-dev.git vendor/tarkov-dev
git submodule update --init --recursive

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate.bat
# On Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

## 📖 Usage

### Starting the Application

1. **Activate the virtual environment:**
   ```bash
   venv\Scripts\activate.bat
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to the local URL shown (typically `http://localhost:8501`)

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

This project is **not affiliated with or endorsed by Battlestate Games**. Escape from Tarkov is a trademark of Battlestate Games Limited.

Use at your own risk. This tool does not modify game files or memory and only reads publicly accessible log files and screenshots.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

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

**Built with ❤️ for the Tarkov community**
