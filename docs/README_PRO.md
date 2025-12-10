## AudioCleaner PRO - SE Removal Edition

<div align="center">

**AI-Powered Audio Enhancement with Sound Effects Removal**

[Standard Version](README.md) | **PRO Version** | [Installation](#installation)

</div>

---

## What's New in PRO

### 🎯 Sound Effects (SE) Removal

The PRO version adds advanced SE removal capabilities to eliminate non-speech sounds:

- **Door slams** 🚪
- **Applause** 👏
- **Camera shutters** 📷
- **Footsteps** 👣
- **Keyboard typing** ⌨️
- **Beep sounds** 🔊
- **Background music** 🎵

### 🚀 Processing Pipelines

**Mode M (BGM Removal with Demucs) - RECOMMENDED**
```
Input Audio
    ↓
Demucs (High-Quality Vocal Extraction)
    - Uses htdemucs model
    - Two-stems separation (vocals/no_vocals)
    - MPS (GPU) acceleration with CPU fallback
    ↓
Clean Output (Voice Only, BGM Removed)
```

**Standard Modes (0, 1, 2)**
```
Input Audio
    ↓
Denoiser (Noise Reduction)
    ↓
VoiceFixer (Quality Enhancement)
    ↓
Clean Output
```

### 📊 Technology Stack

| Component | Purpose | License |
|-----------|---------|---------|
| **Demucs** | BGM/music separation (Mode M) | MIT |
| **AudioSep** | Text-guided sound separation | MIT |
| **SepFormer-DNS** | Post-processing enhancement | Apache-2.0 |
| **Denoiser** | Noise reduction | CC-BY-NC 4.0 |
| **VoiceFixer** | Quality enhancement | MIT |

---

## Processing Modes

### Standard Modes (from base version)

- **Mode 0**: Standard (Denoiser + VoiceFixer)
- **Mode 1**: High Noise
- **Mode 2**: Severely Degraded
- **Mode D**: Denoiser Only

### Advanced Modes

- **Mode M**: BGM Removal (Demucs High-Quality) ⭐ RECOMMENDED
  - High-quality vocal extraction using Demucs
  - Best-in-class music/BGM separation
  - MPS (GPU) acceleration on Apple Silicon
  - Best for: Music removal, podcast with intro/outro BGM
  - Processing time: ~1.5-2x longer than standard
  - Output: Clean vocals with BGM completely removed

- **Mode D**: Denoiser Only
  - Basic noise reduction without quality enhancement
  - Best for: Quick cleaning, testing
  - Processing time: ~same as standard mode

---

## Installation

### Quick Install

```bash
cd AudioCleaner
chmod +x install_pro.sh
./install_pro.sh
```

### What Gets Installed

1. **Base tools** (Denoiser, VoiceFixer)
2. **AudioSep** (~2GB model download)
3. **SpeechBrain/SepFormer-DNS** (~500MB model download)

### Manual Installation

If you prefer manual control:

```bash
# Activate virtual environment
source venv/bin/activate

# Install PyTorch with compatible TorchAudio (< 2.9 for SpeechBrain compatibility)
pip install "torch>=2.0.0,<3.0.0" "torchaudio>=2.0.0,<2.9.0"

# Install dependencies
pip install -r requirements_pro.txt

# Install AudioSep from GitHub (not available on PyPI)
pip install "git+https://github.com/Audio-AGI/AudioSep.git"

# Install SpeechBrain
pip install "speechbrain>=0.5.16"

# Verify installation
python3 -c "from pipeline import build_audiosep; print('AudioSep OK')"
python3 -c "from speechbrain.inference.separation import SepformerSeparation; print('SpeechBrain OK')"
```

**Important Notes**:
- AudioSep is **not available on PyPI**, must install from GitHub
- TorchAudio 2.9+ has breaking changes, use < 2.9 for SpeechBrain compatibility
- First run will download models (~2.5GB total)

---

## Usage

### Basic Usage

```bash
./audio_cleaner_pro.command
```

Then:
1. Drag and drop your audio file
2. Select **Mode S** for SE removal
3. Wait for processing (takes longer than standard modes)
4. Find your cleaned file

### Use Cases

#### Podcast/Video with Background Music (NEW!)

**Problem**: Content has background music that obscures speech

**Solution**:
```
Mode M (BGM Removal with Demucs)
→ High-quality vocal extraction, complete BGM removal
```

**Expected time**: 5 min audio → ~8-10 min processing (with MPS/GPU)
**Best for**: YouTube content, podcasts with intro/outro music, presentations

#### Interview with Background Noise

**Problem**: Recorded interview has general background noise

**Solution**:
```
Mode 0 or 1 (Standard Pipeline)
→ Denoiser + VoiceFixer for noise reduction and quality enhancement
```

**Expected time**: 5 min audio → ~5-8 min processing

#### Podcast with Applause

**Problem**: Podcast has audience applause that obscures speech

**Solution**:
```
Mode A (AudioSep Only)
→ Extracts speech, removes applause
```

**Expected time**: 5 min audio → ~5-8 min processing

#### Field Recording

**Problem**: Outdoor recording with traffic, wind, environmental sounds

**Solution**:
```
Mode S (Full Pipeline)
→ Comprehensive cleaning and enhancement
```

**Expected time**: 5 min audio → ~12-18 min processing

---

## Technical Details

### AudioSep

**How it works**: Uses text descriptions to separate specific sounds

**Supported queries**:
- `"human speech"` - Extract speech
- `"male voice"` - Extract male voice specifically  
- `"female voice"` - Extract female voice specifically
- Custom SE removal (by extracting then subtracting)

**Requirements**:
- 32kHz processing
- ~2GB model
- CPU-only (no GPU required)

### SepFormer-DNS

**How it works**: Enhancement model trained on DNS Challenge dataset

**Features**:
- Removes residual noise
- Enhances speech clarity
- Reduces reverb
- Improves overall quality

**Requirements**:
- 16kHz processing
- ~500MB model
- CPU-only

### Processing Pipeline Details

```python
# Conceptual flow
audio_input = load("input.wav")  # Any format

# Step 1: Denoiser (basic noise removal)
denoised = denoiser.process(audio_input)
# Output: 48kHz, noise reduced

# Step 2: AudioSep (SE removal)
speech_only = audiosep.separate(
    denoised, 
    text="human speech"
)
# Output: 32kHz, speech extracted

# Step 3: SepFormer (enhancement)
enhanced = sepformer.enhance(speech_only)
# Output: 16kHz, quality improved

save(enhanced, "output.wav")
```

---

## Performance

### Processing Time (M1 MacBook Pro)

| Audio Length | Standard Mode | SE Removal Mode |
|--------------|---------------|-----------------|
| 1 minute     | 30-60s        | 2-3 min         |
| 5 minutes    | 3-5 min       | 10-15 min       |
| 10 minutes   | 6-10 min      | 20-30 min       |
| 30 minutes   | 20-30 min     | 60-90 min       |

### Memory Usage

- **Standard mode**: ~2-3GB RAM
- **SE Removal mode**: ~4-6GB RAM (peak during AudioSep)

### Disk Space

- Base installation: ~3-4GB
- With PRO features: ~6-8GB (includes models)

---

## Troubleshooting

### "AudioSep not found" or "No module named 'pipeline'"

AudioSep must be installed from GitHub:

```bash
cd ~/HotDoc/AudioCleaner
source venv/bin/activate
pip install "git+https://github.com/Audio-AGI/AudioSep.git"
```

### "SpeechBrain not found" or TorchAudio compatibility error

Install compatible versions:

```bash
cd ~/HotDoc/AudioCleaner
source venv/bin/activate
pip install "torch>=2.0.0,<3.0.0" "torchaudio>=2.0.0,<2.9.0" --force-reinstall
pip install "speechbrain>=0.5.16" --upgrade
```

### Error: `AttributeError: module 'torchaudio' has no attribute 'list_audio_backends'`

This means TorchAudio 2.9+ is installed. Downgrade:

```bash
cd ~/HotDoc/AudioCleaner
source venv/bin/activate
pip install "torchaudio<2.9.0" --force-reinstall
```

### Processing is Very Slow

This is expected. SE removal requires:
- Multiple model passes
- Large models
- CPU processing

Tips to speed up:
- Use **Mode A** instead of **Mode S** if you don't need full pipeline
- Close other applications
- Process shorter segments

### Poor SE Removal Results

Try:
1. **Different source quality**: AudioSep works best with clear SE sounds
2. **Adjust expectations**: Some SEs overlap with speech frequencies
3. **Manual editing**: For critical work, combine with manual audio editing
4. **Multiple passes**: Run Mode S, then run again on output if needed

### Out of Memory

If you get OOM errors:
- Close other applications
- Process shorter audio segments
- Use standard modes (0, 1, 2) instead of PRO modes

---

## Comparison: Standard vs PRO

| Feature | Standard | PRO |
|---------|----------|-----|
| Noise reduction | ✅ | ✅ |
| Audio enhancement | ✅ | ✅ |
| SE removal | ❌ | ✅ |
| Text-guided separation | ❌ | ✅ |
| Advanced enhancement | ❌ | ✅ |
| Processing time | Fast | Slower |
| Model size | ~3-4GB | ~6-8GB |

---

## When to Use Each Mode

### Use Standard Modes (0, 1, 2) when:
- ✅ Audio has general background noise
- ✅ No specific sound effects to remove
- ✅ No background music
- ✅ Speed is important
- ✅ Basic quality improvement needed

### Use Mode M when: ⭐ RECOMMENDED for BGM removal
- ✅ Audio has background music
- ✅ YouTube videos with BGM
- ✅ Podcasts with intro/outro music
- ✅ Presentations with background music
- ✅ Live recordings with BGM
- ✅ Need clean vocal extraction
- ✅ Have M1/M2/M3 Mac (MPS acceleration)

### Use Mode D when:
- ✅ Only need basic noise reduction
- ✅ Want fast processing
- ✅ Testing audio quality
- ✅ Don't need VoiceFixer enhancement

---

## Advanced: Command-Line Usage

### AudioSep Direct

```bash
source venv/bin/activate
python3 scripts/run_audiosep.py input.wav -o output.wav -q "human speech"
```

### SepFormer Direct

```bash
source venv/bin/activate
python3 scripts/run_sepformer.py input.wav -o output.wav
```

### Custom Pipeline

```bash
# Step 1: Denoise
python3 scripts/run_clearSound.py input.wav -o step1.wav -q high

# Step 2: SE removal
python3 scripts/run_audiosep.py step1.wav -o step2.wav -q "human speech"

# Step 3: Enhance
python3 scripts/run_sepformer.py step2.wav -o final.wav
```

---

## Research References

### AudioSep

**Paper**: "Separate Anything You Describe"  
**Authors**: Audio-AGI Team  
**Code**: https://github.com/Audio-AGI/AudioSep  
**License**: MIT

```bibtex
@article{liu2023separate,
  title={Separate Anything You Describe},
  author={Liu, Xubo and Kong, Qiuqiang and Zhao, Yan and others},
  journal={arXiv preprint arXiv:2308.05037},
  year={2023}
}
```

### SepFormer-DNS

**Paper**: "Attention is All You Need in Speech Separation"  
**Framework**: SpeechBrain  
**Model**: https://huggingface.co/speechbrain/sepformer-dns4-16k-enhancement  
**License**: Apache-2.0

```bibtex
@inproceedings{subakan2021attention,
  title={Attention is All You Need in Speech Separation},
  author={Subakan, Cem and Ravanelli, Mirco and Cornell, Samuele and others},
  booktitle={ICASSP 2021},
  year={2021}
}
```

---

## FAQ

### Q: Can I use GPU for faster processing?

**A**: Currently, CPU-only for stability. GPU support planned for future versions.

### Q: What's the quality difference vs manual editing?

**A**: AI cleaning is consistent and fast, but manual editing gives more control. Best practice: AI clean first, then manual refinement if needed.

### Q: Can I remove specific words/phrases?

**A**: No, this removes sound effects and noise, not specific speech content.

### Q: Does it work with music?

**A**: Partially. AudioSep can separate music from speech, but it's optimized for SE removal from speech recordings.

### Q: Can I batch process files?

**A**: Not yet. Planned for v1.2. Current workaround: use the "F" option to change files without restarting.

---

## Support

### Getting Help

1. Check [README.md](README.md) for base features
2. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues
3. Open an issue on GitHub with:
   - Mode used
   - Input file characteristics
   - Error messages
   - System info

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

### License

Same as base version: MIT License with third-party acknowledgments

---

## Roadmap

### v1.2 (Planned)
- [ ] Batch processing
- [ ] GPU acceleration
- [ ] Custom SE lists
- [ ] Quality metrics (DNSMOS)

### v1.3 (Planned)
- [ ] Target speaker extraction (SpeakerBeam)
- [ ] AV-TSE (with video input)
- [ ] Real-time processing mode

---

**Made with ❤️ for professional audio cleaning**

*For standard version, see [README.md](README.md)*

