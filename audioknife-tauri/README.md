# AudioKnife

**Apple Silicon Optimized Audio Processor**

AudioKnife is a high-performance audio processing application built with Tauri (Rust) and optimized for Apple Silicon Macs. It combines native Rust audio processing with AI-powered enhancement via Python backend.

## Features

### Native Rust Processing (Fast)
- **Silence Padding**: Add silence before/after audio with native Rust speed
- **Format Conversion**: Convert between WAV, MP3, AAC, FLAC, OGG
- **Batch Processing**: Process multiple files in parallel using Rayon

### AI Enhancement (Python Backend)
- **Resemble Enhance**: Denoise and enhance audio quality
- **Demucs**: BGM/vocal separation
- **Spleeter**: Multi-track source separation
- **MP-SENet**: Speech enhancement
- **MossFormer2**: Speaker separation

## Apple Silicon Optimization

- **MPS Backend**: Automatic Apple GPU acceleration via Metal Performance Shaders
- **Unified Memory**: Efficient memory usage on Apple Silicon
- **ARM64 Native**: Compiled specifically for Apple Silicon

## Requirements

### For Tauri App
- macOS 11.0+ (Big Sur or later)
- Rust 1.70+
- Node.js 18+
- FFmpeg (for format conversion)

### For AI Backend
- Python 3.10+
- PyTorch 2.0+ with MPS support
- ~4GB RAM for AI models

## Installation

### 1. Install Dependencies

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Node.js (via Homebrew)
brew install node

# Install FFmpeg
brew install ffmpeg
```

### 2. Build Tauri App

```bash
cd audioknife-tauri

# Install npm dependencies
npm install

# Development mode
npm run tauri dev

# Build for production
npm run tauri build
```

### 3. Setup Python AI Backend (Optional)

```bash
cd python-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python server.py
```

## Usage

### GUI Application
1. Launch AudioKnife
2. Select the "Silence Padding" tab
3. Upload an audio file
4. Set pre-silence and post-silence durations
5. Choose output format
6. Click "Add Silence Padding"

### AI Enhancement
1. Start the Python backend: `python python-backend/server.py`
2. Switch to "AI Enhancement" tab
3. Select processing mode
4. Process your audio

## Architecture

```
AudioKnife/
├── src-tauri/           # Rust backend
│   ├── src/
│   │   ├── audio/       # Native audio processing
│   │   ├── ai_bridge/   # Python IPC
│   │   └── commands.rs  # Tauri commands
│   └── Cargo.toml
├── src/                 # React frontend
├── python-backend/      # AI processing server
└── package.json
```

## Performance Comparison

| Feature | Gradio (Python) | AudioKnife (Tauri) |
|---------|-----------------|-------------------|
| Startup | 3-5 seconds | < 0.5 seconds |
| Memory | ~500MB | ~80MB |
| Batch Processing | Sequential | Parallel |
| GPU Acceleration | Manual | Automatic (MPS) |

## License

MIT License

## Credits

- Built with [Tauri](https://tauri.app/)
- Audio processing with [hound](https://github.com/ruuda/hound) and [FFmpeg](https://ffmpeg.org/)
- AI models: Resemble AI, Meta AI, Deezer Research
