#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    AudioCleaner PRO Installation     ║${NC}"
echo -e "${CYAN}║    + SE Removal Features             ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
echo -e "${BLUE}[1/7]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Found Python ${PYTHON_VERSION}${NC}"

# Create virtual environment for base tools
echo ""
echo -e "${BLUE}[2/7]${NC} Setting up base environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created virtual environment${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate and install base dependencies
source venv/bin/activate

echo -e "${BLUE}[3/7]${NC} Installing base dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install PyTorch with compatible TorchAudio version (< 2.9 for SpeechBrain compatibility)
echo "Installing PyTorch and TorchAudio (compatible versions)..."
pip install "torch>=2.0.0,<3.0.0" "torchaudio>=2.0.0,<2.9.0"

echo "Installing other dependencies..."
pip install -r requirements_pro.txt

echo -e "${GREEN}✓ Base dependencies installed${NC}"

# Install AudioSep from GitHub
echo ""
echo -e "${BLUE}[4/7]${NC} Installing AudioSep from GitHub..."
echo "AudioSep enables text-guided audio separation for SE removal"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    echo "Please install git to continue"
    exit 1
fi

# Clone and install AudioSep from GitHub
echo "Cloning AudioSep repository..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

git clone https://github.com/Audio-AGI/AudioSep.git
cd AudioSep

echo "Installing AudioSep..."
pip install -e . || {
    echo -e "${YELLOW}Warning: AudioSep installation failed${NC}"
    echo -e "${YELLOW}Trying alternative method...${NC}"
    pip install "git+https://github.com/Audio-AGI/AudioSep.git" || {
        echo -e "${RED}AudioSep installation failed with both methods${NC}"
        cd "$SCRIPT_DIR"
        rm -rf "$TEMP_DIR"
    }
}

cd "$SCRIPT_DIR"
rm -rf "$TEMP_DIR"

if python3 -c "import pipeline; from pipeline import build_audiosep" 2>/dev/null; then
    echo -e "${GREEN}✓ AudioSep installed successfully${NC}"
    
    # Pre-download AudioSep model
    echo "Pre-downloading AudioSep model (this may take a few minutes, ~2GB)..."
    python3 << 'PYCODE'
try:
    from pipeline import build_audiosep
    import torch
    import os
    
    # Create checkpoint directory
    os.makedirs("checkpoint", exist_ok=True)
    
    device = torch.device('cpu')
    print("Building AudioSep model...")
    model = build_audiosep(
        config_yaml='config/audiosep_base.yaml',
        checkpoint_path='checkpoint/audiosep_base_4M_steps.ckpt',
        device=device
    )
    print("✓ Model downloaded successfully")
except Exception as e:
    print(f"Note: Model will be downloaded on first use - {e}")
PYCODE
else
    echo -e "${YELLOW}⚠ AudioSep not available${NC}"
    echo -e "${YELLOW}You can try installing it manually later:${NC}"
    echo -e "${YELLOW}  pip install 'git+https://github.com/Audio-AGI/AudioSep.git'${NC}"
fi

# Install SpeechBrain (for SepFormer-DNS)
echo ""
echo -e "${BLUE}[5/7]${NC} Installing SpeechBrain (SepFormer-DNS)..."
echo "SepFormer-DNS provides post-processing enhancement"

# SpeechBrain should already be installed from requirements_pro.txt
# Verify installation
if python3 -c "import speechbrain" 2>/dev/null; then
    echo -e "${GREEN}✓ SpeechBrain already installed${NC}"
    
    # Verify TorchAudio compatibility
    echo "Checking TorchAudio compatibility..."
    python3 << 'PYCODE'
import sys
try:
    import torchaudio
    version = torchaudio.__version__
    major_version = int(version.split('.')[0])
    minor_version = int(version.split('.')[1]) if len(version.split('.')) > 1 else 0
    
    print(f"TorchAudio version: {version}")
    
    # Check if version is < 2.9 (compatible)
    if major_version < 2 or (major_version == 2 and minor_version < 9):
        print("✓ TorchAudio version is compatible with SpeechBrain")
    else:
        print(f"Warning: TorchAudio {version} may have compatibility issues")
        print("Recommended: TorchAudio < 2.9")
        sys.exit(1)
        
except Exception as e:
    print(f"Error checking TorchAudio: {e}")
    sys.exit(1)
PYCODE
    
    if [ $? -eq 0 ]; then
        # Pre-download SepFormer model
        echo "Pre-downloading SepFormer-DNS model (this may take a few minutes, ~500MB)..."
        python3 << 'PYCODE'
try:
    from speechbrain.inference.separation import SepformerSeparation as Separator
    import torch
    
    print("Downloading model...")
    model = Separator.from_hparams(
        source="speechbrain/sepformer-dns4-16k-enhancement",
        savedir="pretrained_models/sepformer-dns4",
        run_opts={"device": "cpu"}
    )
    print("✓ Model downloaded successfully")
except Exception as e:
    print(f"Note: Model will be downloaded on first use")
    print(f"Error details: {e}")
PYCODE
    fi
else
    echo -e "${YELLOW}⚠ SpeechBrain not available${NC}"
    echo "Attempting to install..."
    pip install "speechbrain>=0.5.16" || {
        echo -e "${RED}SpeechBrain installation failed${NC}"
        echo -e "${YELLOW}You can try installing it manually later:${NC}"
        echo -e "${YELLOW}  pip install speechbrain${NC}"
    }
fi

# Setup Denoiser
echo ""
echo -e "${BLUE}[6/7]${NC} Setting up Denoiser..."
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
PYCODE

deactivate

# Setup VoiceFixer
echo ""
echo -e "${BLUE}[7/7]${NC} Checking VoiceFixer installation..."
VOICEFIXER_DIR="$HOME/voicefixer_app"

if [ ! -d "$VOICEFIXER_DIR" ]; then
    echo -e "${YELLOW}VoiceFixer not found at ${VOICEFIXER_DIR}${NC}"
    echo "Auto-installing VoiceFixer..."
    
    mkdir -p "$VOICEFIXER_DIR"
    cd "$VOICEFIXER_DIR"
    
    python3 -m venv venv
    source venv/bin/activate
    
    pip install --upgrade pip > /dev/null 2>&1
    pip install voicefixer || {
        echo -e "${YELLOW}Warning: VoiceFixer installation failed${NC}"
        deactivate
        cd "$SCRIPT_DIR"
        echo -e "${YELLOW}You can install it later manually${NC}"
        return 0
    }
    
    if python3 -c "from voicefixer import VoiceFixer" 2>/dev/null; then
        echo -e "${GREEN}✓ VoiceFixer installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠ VoiceFixer installation may be incomplete${NC}"
    fi
    
    deactivate
    cd "$SCRIPT_DIR"
else
    echo -e "${GREEN}✓ VoiceFixer found${NC}"
fi

# Create requirements_pro.txt
cat > requirements_pro.txt << 'EOF'
# Core Dependencies (same as base)
torch>=1.10.0
torchaudio>=0.10.0
soundfile>=0.10.3
librosa>=0.9.0
scipy>=1.7.0
numpy>=1.21.0

# Denoiser Dependencies
julius>=0.2.6
pesq>=0.0.3
pystoi>=0.3.3

# AudioSep (SE Removal)
# Install: pip install audiosep
# Note: Requires ~2GB for model

# SpeechBrain (SepFormer-DNS Enhancement)
speechbrain>=0.5.0
# Note: Requires ~500MB for model

# Utilities
tqdm>=4.62.0
matplotlib>=3.5.0
EOF

# Final checks and summary
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PRO Installation Complete!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check what was actually installed
source venv/bin/activate

echo -e "Installed features:"
echo -e "  ✓ Standard cleaning (Denoiser + VoiceFixer)"

if python3 -c "from audiosep import AudioSep" 2>/dev/null; then
    echo -e "  ✓ SE Removal (AudioSep)"
else
    echo -e "  ⚠ SE Removal (AudioSep) - not installed"
fi

if python3 -c "import speechbrain" 2>/dev/null; then
    echo -e "  ✓ Enhancement (SepFormer-DNS)"
else
    echo -e "  ⚠ Enhancement (SepFormer-DNS) - not installed"
fi

deactivate

# Check for Demucs (external dependency for Mode M)
echo ""
echo -e "External dependencies:"
if command -v demucs &> /dev/null; then
    echo -e "  ✓ Demucs (for Mode M - BGM removal)"
else
    echo -e "  ⚠ Demucs not found (Mode M will not work)"
    echo -e "    To install: ${YELLOW}python3 -m pip install demucs${NC}"
    echo -e "    Or refer to: https://github.com/facebookresearch/demucs"
fi

echo ""
echo -e "To run AudioCleaner PRO:"
echo -e "  ${BLUE}./audio_cleaner_pro.command${NC}"
echo ""
echo -e "For help, see:"
echo -e "  ${BLUE}README_PRO.md${NC}"
echo ""

# Make main script executable
chmod +x audio_cleaner_pro.command

echo -e "${GREEN}Ready to use! 🎵✨${NC}"

