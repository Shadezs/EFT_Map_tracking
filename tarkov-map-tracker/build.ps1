# PyInstaller Build Script
# Creates a standalone executable for Windows

# Build command
pyinstaller --onefile `
    --name "TarkovMapTracker" `
    --icon icon.ico `
    --add-data "config.yaml;." `
    --add-data "vendor;vendor" `
    --hidden-import streamlit `
    --hidden-import folium `
    --hidden-import streamlit_folium `
    app.py

Write-Host "Build complete! Check the 'dist' folder for TarkovMapTracker.exe"
