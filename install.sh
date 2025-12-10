#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    AudioCleaner Installation         ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
echo -e "${BLUE}[1/5]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Found Python ${PYTHON_VERSION}${NC}"

# Create virtual environment for Denoiser
echo ""
echo -e "${BLUE}[2/5]${NC} Setting up Denoiser environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created virtual environment${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate and install Denoiser dependencies
source venv/bin/activate

echo -e "${BLUE}[3/5]${NC} Installing Denoiser dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "Installing PyTorch and TorchAudio..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

echo "Installing other dependencies (this may take a few minutes)..."
# Install requirements, but continue even if pesq fails (it's not essential)
pip install -r requirements.txt || {
    echo -e "${YELLOW}Warning: Some optional packages failed to install${NC}"
    echo -e "${YELLOW}Attempting to install essential packages only...${NC}"
    pip install soundfile librosa scipy numpy julius pystoi tqdm matplotlib
}

echo -e "${GREEN}✓ Denoiser dependencies installed${NC}"

# Download Denoiser model
echo ""
echo -e "${BLUE}[4/5]${NC} Setting up Denoiser model..."
mkdir -p denoiser/pretrained

if [ ! -d "denoiser/denoiser" ]; then
    echo "Cloning Denoiser repository..."
    git clone https://github.com/facebookresearch/denoiser.git temp_denoiser
    cp -r temp_denoiser/denoiser denoiser/
    rm -rf temp_denoiser
fi

# Download pre-trained model
python3 << 'PYCODE'
import sys
sys.path.insert(0, 'denoiser')
try:
    from denoiser import pretrained
    print("Downloading DNS64 model...")
    model = pretrained.dns64()
    print("✓ Model downloaded successfully")
except Exception as e:
    print(f"Note: Model will be downloaded on first use")
    print(f"Details: {e}")
PYCODE

deactivate

# Setup VoiceFixer
echo ""
echo -e "${BLUE}[5/5]${NC} Checking VoiceFixer installation..."
VOICEFIXER_DIR="$HOME/voicefixer_app"

if [ ! -d "$VOICEFIXER_DIR" ]; then
    echo -e "${YELLOW}VoiceFixer not found at ${VOICEFIXER_DIR}${NC}"
    read -p "Would you like to install VoiceFixer? [Y/n]: " install_vf
    
    if [[ ! "$install_vf" =~ ^[Nn]$ ]]; then
        echo "Installing VoiceFixer..."
        mkdir -p "$VOICEFIXER_DIR"
        cd "$VOICEFIXER_DIR"
        
        python3 -m venv venv
        source venv/bin/activate
        
        pip install --upgrade pip
        pip install voicefixer
        
        # Test installation
        python3 -c "from voicefixer import VoiceFixer; print('VoiceFixer installed successfully')"
        
        deactivate
        cd "$SCRIPT_DIR"
        echo -e "${GREEN}✓ VoiceFixer installed${NC}"
    else
        echo -e "${YELLOW}Skipping VoiceFixer installation${NC}"
        echo -e "${YELLOW}Note: You can use Denoiser-only mode (D)${NC}"
    fi
else
    echo -e "${GREEN}✓ VoiceFixer found${NC}"
fi

# Final checks
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "To run AudioCleaner:"
echo -e "  ${BLUE}./audio_cleaner.command${NC}"
echo ""
echo -e "For help, see:"
echo -e "  ${BLUE}README.md${NC}"
echo ""

# Make main script executable
chmod +x audio_cleaner.command

echo -e "${GREEN}Ready to use! 🎵${NC}"

