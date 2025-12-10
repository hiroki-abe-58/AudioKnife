# AudioCleaner PRO - Changelog

## [1.1.0-PRO] - 2025-11-03

### 🎉 Major Release: SE Removal Support

This release adds advanced sound effects (SE) removal capabilities to AudioCleaner.

### Added

#### New Processing Pipeline
- **Mode S**: Full SE Removal Pipeline
  - Denoiser → AudioSep → SepFormer-DNS
  - Removes door slams, applause, footsteps, keyboard, camera shutters, beeps
  - Best quality output for speech with environmental sounds

- **Mode A**: AudioSep Only Mode
  - Text-guided audio separation
  - Faster than Mode S
  - Flexible sound extraction

#### New Components

1. **AudioSep Integration** (`scripts/run_audiosep.py`)
   - Text-guided audio separation
   - Extracts human speech from mixed audio
   - Supports custom text queries
   - MIT License
   - Model: ~2GB download

2. **SepFormer-DNS Integration** (`scripts/run_sepformer.py`)
   - Post-processing enhancement
   - Trained on DNS Challenge dataset
   - Removes residual noise and improves clarity
   - Apache-2.0 License
   - Model: ~500MB download

3. **AudioCleaner PRO** (`audio_cleaner_pro.command`)
   - Enhanced main script with SE removal modes
   - Backward compatible with standard modes (0, 1, 2, D)
   - New modes: S (SE Removal), A (AudioSep)

#### Installation & Documentation

- **install_pro.sh**: Automated PRO installation script
  - Installs AudioSep
  - Installs SpeechBrain/SepFormer-DNS
  - Pre-downloads models
  - Interactive configuration

- **README_PRO.md**: Comprehensive PRO documentation
  - SE removal use cases
  - Processing pipeline details
  - Performance benchmarks
  - Troubleshooting guide
  - Research references

- **requirements_pro.txt**: PRO dependencies list

### Technical Details

#### AudioSep
- **Purpose**: Text-guided sound separation
- **Use Case**: Remove specific SEs (applause, doors, footsteps, etc.)
- **Input**: 32kHz audio
- **Processing**: CPU-only, ~2-3min per 5min audio
- **Based on**: "Separate Anything You Describe" paper

#### SepFormer-DNS
- **Purpose**: Post-processing speech enhancement
- **Use Case**: Clean up residual noise and improve quality
- **Input**: 16kHz audio
- **Processing**: CPU-only, ~1-2min per 5min audio
- **Based on**: "Attention is All You Need in Speech Separation" paper

### Processing Modes Comparison

| Mode | Pipeline | Use Case | Speed |
|------|----------|----------|-------|
| 0-2 | Denoiser + VoiceFixer | General noise | Fast |
| D | Denoiser only | Quick denoise | Fastest |
| S | Denoiser + AudioSep + SepFormer | SE removal | Slow |
| A | AudioSep + SepFormer | Clean source with SE | Medium |

### Performance Impact

- **Standard modes**: No change
- **Mode S**: 2-3x processing time vs standard
- **Mode A**: 1.5x processing time vs standard
- **Memory**: +2-3GB peak usage in PRO modes
- **Disk**: +3-4GB for models

### Compatibility

- ✅ Fully backward compatible with v1.0
- ✅ Standard modes (0, 1, 2, D) work identically
- ✅ Can run both `audio_cleaner.command` and `audio_cleaner_pro.command`
- ✅ PRO features optional (skip installation if not needed)

### Known Limitations

1. **CPU-only processing**: No GPU acceleration yet
2. **No batch mode**: Process files one at a time
3. **SE overlap**: If SE and speech frequencies overlap significantly, some SE may remain
4. **Processing time**: Mode S is significantly slower than standard modes
5. **Model downloads**: First run requires internet for model download

### Upgrade Path

#### From v1.0 to v1.1-PRO

```bash
cd AudioCleaner

# Run PRO installer (keeps v1.0 intact)
./install_pro.sh

# Both versions available:
./audio_cleaner.command      # v1.0 (standard)
./audio_cleaner_pro.command  # v1.1 (PRO)
```

### Dependencies Added

```
audiosep>=1.0.0           # AudioSep for SE removal
speechbrain>=0.5.0        # SepFormer-DNS enhancement
```

### File Structure Changes

```
AudioCleaner/
├── audio_cleaner.command          # v1.0 (unchanged)
├── audio_cleaner_pro.command      # v1.1 (NEW)
├── install.sh                     # v1.0 installer (unchanged)
├── install_pro.sh                 # v1.1 installer (NEW)
├── README.md                      # v1.0 docs (unchanged)
├── README_PRO.md                  # v1.1 docs (NEW)
├── CHANGELOG_PRO.md               # This file (NEW)
├── requirements.txt               # v1.0 deps (unchanged)
├── requirements_pro.txt           # v1.1 deps (NEW)
└── scripts/
    ├── run_clearSound.py          # v1.0 (unchanged)
    ├── run_audiosep.py            # v1.1 (NEW)
    └── run_sepformer.py           # v1.1 (NEW)
```

### Migration Notes

- **No breaking changes**: v1.0 functionality unchanged
- **Optional upgrade**: PRO features are additive
- **Separate scripts**: Can use both versions
- **Shared models**: Denoiser model shared between versions

### Testing

Tested on:
- macOS 13 (Ventura) / M1 MacBook Pro
- macOS 14 (Sonoma) / M2 MacBook Air
- Python 3.9, 3.10, 3.11

### Contributors

- Core development: AudioCleaner Team
- AudioSep integration: Based on Audio-AGI/AudioSep
- SepFormer integration: Based on SpeechBrain

### Acknowledgments

Special thanks to:
- **Audio-AGI Team** for AudioSep
- **SpeechBrain Team** for SepFormer-DNS
- **Facebook Research** for Denoiser
- **VoiceFixer Team** for VoiceFixer

---

## [1.0.0] - 2025-11-03

Initial release - see [CHANGELOG.md](CHANGELOG.md)

---

## Upcoming

### v1.2 (Planned)
- [ ] Batch processing mode
- [ ] GPU acceleration support
- [ ] Custom SE type lists
- [ ] Quality metrics (DNSMOS P.835)
- [ ] Progress bars for long files
- [ ] Configuration file support

### v1.3 (Planned)
- [ ] Target Speaker Extraction (SpeakerBeam/SpEx+)
- [ ] Speaker enrollment (reference audio)
- [ ] AV-TSE (audio-visual target speech extraction)
- [ ] Real-time processing mode
- [ ] DeepFilterNet integration

### v2.0 (Future)
- [ ] Web GUI interface
- [ ] Cloud processing API
- [ ] Multi-language support beyond English/Japanese
- [ ] Plugin system for custom processors
- [ ] Workspace/project management

---

## Version Numbering

**Format**: MAJOR.MINOR.PATCH[-EDITION]

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes
- **EDITION**: PRO, LITE, etc.

Examples:
- `1.0.0`: Base version
- `1.1.0-PRO`: PRO edition with SE removal
- `1.1.1-PRO`: PRO edition bug fix

---

## Getting Help

- **Installation issues**: Check `install_pro.sh` output
- **Usage questions**: See [README_PRO.md](README_PRO.md)
- **Bug reports**: Open GitHub issue with "PRO" label
- **Feature requests**: Open GitHub issue with "enhancement" + "PRO" labels

---

*For standard version changelog, see [CHANGELOG.md](CHANGELOG.md)*

