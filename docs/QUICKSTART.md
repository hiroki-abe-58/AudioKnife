# AudioCleaner Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

Before starting, verify you have:

```bash
# Check Python version (need 3.8+)
python3 --version

# Check git
git --version
```

If Python is not installed, download from [python.org](https://www.python.org/downloads/)

## Installation (2 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/AudioCleaner.git
cd AudioCleaner
```

### Step 2: Run Installer

```bash
chmod +x install.sh
./install.sh
```

The installer will:
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Download AI models
- ✓ Setup VoiceFixer (optional)

**Time**: ~2-3 minutes (depending on internet speed)

### Step 3: Verify Installation

```bash
./audio_cleaner.command
```

You should see:
```
╔═══════════════════════════════════════╗
║    AudioCleaner v1.0                 ║
║    AI-Powered Audio Enhancement      ║
╚═══════════════════════════════════════╝
```

## First Use (2 minutes)

### Process Your First File

1. **Launch**:
   ```bash
   ./audio_cleaner.command
   ```

2. **Add File**:
   - Drag your audio file into the terminal
   - Press Enter

3. **Select Mode**:
   - Press Enter for default (Mode 0)
   - Or type `1` or `2` for more aggressive cleaning

4. **Wait**:
   - Processing takes ~30-60 seconds per minute of audio
   - You'll see real-time progress

5. **Done**!:
   - Find your cleaned file in the same directory
   - Named: `YYYY-MM-DD_HH-MM-SS__filename_cleaned.wav`

## Common First-Time Issues

### "Python not found"

Install Python 3.8 or higher:
```bash
brew install python3  # macOS with Homebrew
```

### "Permission denied"

Make scripts executable:
```bash
chmod +x install.sh audio_cleaner.command
```

### "VoiceFixer not found"

This is optional. You can:
- Skip it and use Denoiser-only mode (D)
- Or install it when prompted

## Next Steps

### Learn More

- **Full Documentation**: See [README.md](README.md)
- **Detailed Usage**: See [docs/USAGE.md](docs/USAGE.md)
- **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### Try Different Modes

| Your Audio | Try Mode |
|------------|----------|
| Clean podcast | 0 (Standard) |
| Noisy recording | 1 (High Noise) |
| Old/degraded audio | 2 (Severely Degraded) |
| Just denoising | D (Denoiser Only) |

### Process Multiple Files

After first file completes:
1. Type `F` to change file
2. Drag new file
3. Select mode
4. Repeat!

## Tips for Best Results

### ✅ DO

- Use highest quality source files
- Start with Mode 0
- Keep original files
- Try different modes if unsatisfied

### ❌ DON'T

- Use heavily compressed MP3s (if possible)
- Expect miracles from extremely poor audio
- Delete originals before checking results
- Process already-processed files repeatedly

## Getting Help

### Quick Troubleshooting

```bash
# Check if installation completed
ls -la venv/

# Verify Python packages
source venv/bin/activate
pip list | grep torch

# Test Denoiser
./scripts/run_clearSound.py --help
```

### Still Stuck?

1. Check [README.md](README.md) troubleshooting section
2. Search [existing issues](https://github.com/yourusername/AudioCleaner/issues)
3. Open a [new issue](https://github.com/yourusername/AudioCleaner/issues/new)

## Example Workflow

### Podcast Production

```bash
# Record episode → raw_episode.wav

# Clean audio
./audio_cleaner.command
# Drag raw_episode.wav
# Mode: 0

# Result → 2025-11-03_14-30-45__raw_episode_cleaned.wav

# Continue editing in DAW
```

### Interview Transcription

```bash
# Phone interview → interview.m4a

# Clean for transcription
./audio_cleaner.command
# Drag interview.m4a
# Mode: 1 (High Noise)

# Upload cleaned version to transcription service
# → Better accuracy!
```

### Archive Restoration

```bash
# Old cassette transfer → cassette_recording.wav

# Restore quality
./audio_cleaner.command
# Drag cassette_recording.wav
# Mode: 2 (Severely Degraded)

# Save to archive with metadata
```

## Performance Expectations

**M1 MacBook Pro** (typical):
- 1 min audio → 30-60 seconds
- 5 min audio → 3-5 minutes
- 10 min audio → 6-10 minutes

**Intel Mac** (older):
- ~1.5-2x slower than M1

**Why so slow?**
- AI models are computationally intensive
- CPU-only processing (for stability)
- High-quality output (48kHz)

## What's Next?

### Explore Features

- [x] Basic cleaning ← You are here!
- [ ] Try different modes
- [ ] Process multiple files
- [ ] Use with your workflow
- [ ] Share your results!

### Contribute

Love AudioCleaner? Consider:
- ⭐ Star on GitHub
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Summary

```bash
# Quick commands to remember:
git clone https://github.com/yourusername/AudioCleaner.git
cd AudioCleaner
./install.sh
./audio_cleaner.command
```

**That's it! You're ready to clean audio. 🎵**

---

*Questions? See [README.md](README.md) or open an issue!*

