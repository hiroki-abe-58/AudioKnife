#!/bin/bash

# AudioCleaner Pro - GUI Launcher
# Gradio-based web interface

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    AudioCleaner Pro - GUI             ║${NC}"
echo -e "${CYAN}║    Web-based Audio Enhancement        ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_DIR"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}[ERROR] Virtual environment not found${NC}"
    echo -e "${YELLOW}Please run install.sh first${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check for Gradio
if ! python3 -c "import gradio" 2>/dev/null; then
    echo -e "${YELLOW}[INFO] Installing Gradio...${NC}"
    pip install gradio --quiet
fi

# Check for app_gui.py
if [ ! -f "app_gui.py" ]; then
    echo -e "${RED}[ERROR] app_gui.py not found${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}[INFO] Starting AudioCleaner Pro GUI...${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  The web interface will open automatically"
echo -e "  Or visit: ${BLUE}http://127.0.0.1:7860${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Open browser after a short delay
(sleep 2 && open "http://127.0.0.1:7860") &

# Run the GUI
python3 app_gui.py --port 7860

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}    AudioCleaner Pro GUI - Goodbye!      ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

