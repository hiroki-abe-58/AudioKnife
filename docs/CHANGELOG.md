# Changelog

All notable changes to AudioCleaner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### Added
- Initial release of AudioCleaner
- Two-stage audio processing pipeline (Denoiser + VoiceFixer)
- Interactive command-line interface
- Four processing modes (Standard, High Noise, Severely Degraded, Denoiser Only)
- Drag-and-drop file input
- Real-time processing feedback
- Audio preview on macOS
- Automatic timestamp-based output naming
- Comprehensive error handling and recovery
- Detailed logging and debug information
- CPU-optimized processing for M1/M2 Macs

### Features
- **Noise Reduction**: Facebook Research Denoiser integration
  - DNS64 pre-trained model
  - Stereo and mono support
  - Adaptive resampling (16kHz → 48kHz)
  - CPU-only processing for stability

- **Audio Enhancement**: VoiceFixer integration
  - Three enhancement modes
  - Automatic fallback mechanism
  - Quality restoration for degraded audio

- **User Experience**:
  - Color-coded terminal interface
  - Progress indicators
  - File change without restart
  - Continuous processing mode

### Documentation
- Comprehensive README (English + Japanese)
- Detailed usage guide
- Architecture documentation
- Contributing guidelines
- MIT License with third-party acknowledgments

### Installation
- Automated installation script
- Virtual environment setup
- Dependency management
- Model download automation

## [Unreleased]

### Planned Features
- [ ] Batch processing mode
- [ ] GUI interface (web-based)
- [ ] Linux and Windows support
- [ ] Configuration file support
- [ ] Progress bars for long files
- [ ] Audio quality metrics
- [ ] Docker container
- [ ] Real-time processing mode
- [ ] Plugin system for custom processors

### Under Consideration
- [ ] Cloud processing API
- [ ] Mobile app companion
- [ ] Advanced EQ controls
- [ ] Spectral analysis visualization
- [ ] A/B comparison tool
- [ ] Preset management
- [ ] Multi-language support
- [ ] Noise profile customization

## Version History

### Version Numbering

- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes and minor improvements

---

## How to Read This Changelog

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

### Links

- [1.0.0]: Initial release
- Compare versions: [GitHub Releases](https://github.com/yourusername/AudioCleaner/releases)

---

*For detailed commit history, see [GitHub Commits](https://github.com/yourusername/AudioCleaner/commits/main)*

