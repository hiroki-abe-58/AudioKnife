# AudioCleaner Usage Guide

## Quick Start

```bash
./audio_cleaner.command
```

## Detailed Workflow

### 1. Launch the Application

```bash
cd AudioCleaner
./audio_cleaner.command
```

You'll see the welcome screen:

```
╔═══════════════════════════════════════╗
║    AudioCleaner v1.0                 ║
║    AI-Powered Audio Enhancement      ║
╚═══════════════════════════════════════╝
```

### 2. Input Your Audio File

When prompted, drag and drop your audio file into the terminal window:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Drag & Drop Audio File Here
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: 
```

The file path will be automatically filled when you drop the file.

### 3. Select Processing Mode

Choose the appropriate mode for your audio:

```
━━━ Select Mode ━━━
0: Standard (Recommended)
1: High Noise
2: Severely Degraded
D: Denoiser Only
F: Select Different File
Q: Quit

Select [Enter=0]:
```

#### Mode Selection Guide

| Input Type | Characteristics | Recommended Mode |
|------------|----------------|------------------|
| **Podcast/Interview** | Clear speech, minimal noise | 0 (Standard) |
| **Field Recording** | Environmental noise | 1 (High Noise) |
| **Phone Recording** | Low quality, compressed | 2 (Severely Degraded) |
| **Studio Recording** | Just needs denoising | D (Denoiser Only) |

### 4. Processing

The tool will process your audio through two stages:

```
Step 1: Denoiser - Noise Reduction
==================================================
[INFO] CPU使うで（安定動作優先）
[Processing] Loading audio...
[INFO] Original audio: 44100Hz, 2ch
[INFO] Resampling for model (44100Hz → 16000Hz)...
[INFO] Stereo detected, processing each channel...
  - Channel 1 processing...
  - Channel 2 processing...
[SUCCESS] Noise reduction complete!

Step 2: VoiceFixer - Audio Enhancement
==================================================
Mode 0: Standard
Processing...
[SUCCESS] Audio enhancement complete!
```

### 5. Output

Your cleaned audio will be saved in the same directory as the input file:

```
✅ Processing complete!
📁 Saved to: /path/to/2025-11-03_14-30-45__myfile_cleaned.wav
```

### 6. Preview (macOS only)

If you're on macOS, you'll be asked if you want to preview the audio:

```
Play processed audio? [y/N]:
```

Type `y` and press Enter to play the audio.

### 7. Continue or Exit

After processing, you can:
- Press Enter to process another file with a different mode
- Type `F` to select a different file
- Type `Q` to quit

## Advanced Usage

### Processing Multiple Files

1. Process your first file
2. When prompted, select `F` (change file)
3. Drag and drop the next file
4. Select mode and process
5. Repeat as needed

### Comparing Modes

To compare different processing modes on the same file:

1. Process with Mode 0
2. When prompted, press Enter (keep same file)
3. Process with Mode 1
4. Compare the outputs

### Command-Line Tips

#### Create an Alias (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias audioclean='/path/to/AudioCleaner/audio_cleaner.command'
```

Then you can run:
```bash
audioclean
```

#### Navigate Faster

Use Tab completion when typing file paths manually.

## Output File Naming

Format: `YYYY-MM-DD_HH-MM-SS__originalname_cleaned.wav`

Examples:
- `2025-11-03_14-30-45__interview_cleaned.wav`
- `2025-11-03_14-35-12__podcast_ep01_cleaned.wav`

This ensures:
- Chronological sorting
- No overwriting of previous outputs
- Clear origin tracking

## Processing Time Estimates

| Audio Length | M1 Mac | Intel Mac |
|--------------|--------|-----------|
| 1 minute | 30-60s | 60-90s |
| 5 minutes | 3-5 min | 5-8 min |
| 10 minutes | 6-10 min | 10-15 min |
| 30 minutes | 20-30 min | 30-45 min |

*Times are approximate and depend on:*
- Audio complexity (mono vs stereo)
- Processing mode
- System load
- File format

## Best Practices

### 1. Start Conservative

- Always try Mode 0 (Standard) first
- Only use higher modes if results are unsatisfactory

### 2. Prepare Your Audio

- Use the highest quality source available
- Avoid pre-processed or heavily compressed files when possible
- Convert to WAV for best results

### 3. Manage Expectations

- Very poor quality audio has limits
- Background music may be affected
- Some artifacts may remain in extreme cases

### 4. Organize Your Workflow

```
project/
├── raw/              # Original recordings
├── cleaned/          # Processed outputs
└── final/            # Post-edited versions
```

### 5. Backup Originals

Always keep your original files! AudioCleaner creates new files rather than overwriting.

## Troubleshooting

### "File not found" Error

- Make sure the file path has no special characters
- Try copying the file to a simpler path
- Use quotes if path has spaces

### Processing Hangs

- Check Activity Monitor for CPU usage
- Close other applications
- Try Denoiser-only mode (D) first

### Poor Results

- Try different modes
- Check if source quality is sufficient
- Consider manual audio editing for extreme cases

## Tips & Tricks

### For Podcasters

1. Record in quiet environment
2. Use Mode 0 for light cleanup
3. Preserve natural voice character

### For Transcription

1. Use Mode 1 or 2 for better clarity
2. Process before sending to transcription service
3. Cleaner audio = better transcription

### For Archival

1. Keep originals separate
2. Use Mode 2 for old recordings
3. Document which mode was used

## Getting Help

- Check [README.md](../README.md) for installation issues
- See [CONTRIBUTING.md](../CONTRIBUTING.md) to report bugs
- Open an issue on GitHub for support

---

**Happy cleaning! 🎵**

