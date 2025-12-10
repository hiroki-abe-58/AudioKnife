# AudioCleaner Architecture

## Overview

AudioCleaner is a two-stage audio processing pipeline that combines noise reduction and audio enhancement.

```
Input Audio → Denoiser → VoiceFixer → Output Audio
              (Stage 1)   (Stage 2)
```

## Components

### 1. Main Script (`audio_cleaner.command`)

**Language**: Bash

**Responsibilities**:
- User interface and interaction
- File input/output handling
- Mode selection
- Python script orchestration
- Audio playback (macOS)

**Flow**:
```
Start
  ↓
Display UI
  ↓
Get Input File ←──────┐
  ↓                   │
Select Mode           │
  ↓                   │
Execute Python Script │
  ↓                   │
Display Results       │
  ↓                   │
Preview Audio?        │
  ↓                   │
Continue? ────────────┘
  ↓
Exit
```

### 2. Processing Script (Embedded Python)

**Language**: Python 3

**Key Functions**:

#### `run_denoiser(input_file, output_file, denoiser_dir)`
- Executes Facebook Research's Denoiser
- Removes background noise
- Returns path to denoised file

#### `run_voicefixer_direct(input_file, output_file, voicefixer_dir, mode)`
- Executes VoiceFixer enhancement
- Improves audio quality
- Supports 3 processing modes

#### `process_audio(input_file, mode, denoiser_dir, voicefixer_dir)`
- Orchestrates the complete pipeline
- Handles temporary files
- Manages error recovery

### 3. Denoiser Module

**Source**: [Facebook Research Denoiser](https://github.com/facebookresearch/denoiser)

**Location**: `scripts/run_clearSound.py`

**Model**: DNS64 (pre-trained)

**Processing**:
```python
# Pseudo-code
load_model()
input_audio = load_audio(input_file)  # e.g., 44100Hz stereo
resampled = resample(input_audio, 16000)  # Model requirement
enhanced = model(resampled)  # Neural processing
upsampled = resample(enhanced, 48000)  # High quality output
save_audio(output_file, upsampled)
```

**Key Features**:
- Encoder-decoder architecture
- Skip connections for better reconstruction
- CPU-optimized (MPS disabled for compatibility)
- Handles mono and stereo

### 4. VoiceFixer Module

**Source**: [VoiceFixer](https://github.com/haoheliu/voicefixer)

**Location**: External (`~/voicefixer_app/`)

**Modes**:
- Mode 0: Standard restoration
- Mode 1: High noise handling
- Mode 2: Severe degradation (with fallback to Mode 0)

**Processing**:
```python
# Pseudo-code
voicefixer = VoiceFixer()
voicefixer.restore(
    input=input_file,
    output=output_file,
    cuda=False,  # CPU-only
    mode=mode
)
```

## Data Flow

### Standard Mode (0, 1, 2)

```
Original File
     ↓
[Temporary Directory Created]
     ↓
Denoiser Processing
     ↓
Temp File (denoised.wav)
     ↓
VoiceFixer Processing
     ↓
Final Output File
     ↓
[Temporary Directory Cleaned]
```

### Denoiser-Only Mode (D)

```
Original File
     ↓
Denoiser Processing
     ↓
Final Output File (no temp)
```

## Error Handling

### Graceful Degradation

```
Try Full Pipeline
     ↓
Denoiser Failed? → Skip to VoiceFixer
     ↓
VoiceFixer Failed? → Keep Denoiser result
     ↓
Both Failed? → Report error
```

### Error Recovery

1. **Missing Components**: Skip stage, warn user
2. **Processing Failure**: Detailed error output
3. **Mode 2 Failure**: Auto-retry with Mode 0
4. **File I/O Errors**: Clear error messages

## File Structure

```
AudioCleaner/
├── audio_cleaner.command    # Main executable
├── scripts/
│   └── run_clearSound.py    # Denoiser wrapper
├── venv/                    # Python environment
│   └── ...
├── denoiser/                # Denoiser library
│   ├── denoiser/           # Core module
│   └── pretrained/         # Models (gitignored)
├── example/                 # Test files
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
├── install.sh              # Setup script
├── .gitignore
├── LICENSE
└── README.md
```

## Dependencies

### Python Packages

```
torch >= 1.10.0          # Deep learning framework
torchaudio >= 0.10.0     # Audio I/O and processing
soundfile >= 0.10.3      # Audio file reading/writing
librosa >= 0.9.0         # Audio analysis
scipy >= 1.7.0           # Scientific computing
numpy >= 1.21.0          # Numerical operations
```

### System Requirements

- Python 3.8+
- 4GB+ RAM
- macOS (primary), Linux/Windows (experimental)

## Performance Considerations

### CPU Usage

Both Denoiser and VoiceFixer are CPU-intensive:
- Multi-threaded processing where possible
- MPS (Metal) disabled for stability
- Scales with audio length

### Memory Usage

- Peak usage during processing: ~2-4GB
- Temporary files cleaned automatically
- Streaming processing for large files (future enhancement)

### Optimization Strategies

1. **Denoiser**: 
   - Process channels separately for stereo
   - Adaptive resampling to minimize quality loss

2. **VoiceFixer**:
   - Fallback mechanism for failed modes
   - Batch processing (not yet implemented)

## Security Considerations

### Input Validation

- File existence checks
- Path sanitization (quotes removed)
- File format validation (delegated to libraries)

### Sandboxing

- No network access during processing
- Temporary files in system temp directory
- Automatic cleanup on exit

### Permissions

- No elevated privileges required
- Read-only access to input files
- Write access to output directory only

## Future Architecture

### Planned Enhancements

1. **Batch Processing**
   ```
   Queue Manager → Worker Pool → Progress Tracker
   ```

2. **GUI Interface**
   ```
   Web Server (Flask/FastAPI)
        ↓
   Browser Interface
        ↓
   WebSocket Updates
   ```

3. **Plugin System**
   ```
   Core Engine ← Plugin Manager → Custom Processors
   ```

4. **Cloud Processing**
   ```
   Local Client → API Gateway → Cloud Workers
   ```

## Testing Strategy

### Unit Tests (Planned)

- Individual function testing
- Mock external dependencies
- Edge case handling

### Integration Tests (Planned)

- End-to-end processing
- Multiple file formats
- Error scenarios

### Performance Tests (Planned)

- Benchmarking different file sizes
- Memory usage profiling
- CPU utilization analysis

## Contributing to Architecture

When modifying the architecture:

1. **Maintain Modularity**: Keep components loosely coupled
2. **Document Changes**: Update this file
3. **Preserve Compatibility**: Support existing file formats
4. **Add Tests**: Cover new functionality
5. **Consider Performance**: Profile before/after changes

## References

### Academic Papers

1. Defossez et al., "Real Time Speech Enhancement in the Waveform Domain", Interspeech 2020
2. Liu et al., "VoiceFixer: Toward General Speech Restoration with Neural Vocoder", 2021

### Implementation References

- [Denoiser Documentation](https://github.com/facebookresearch/denoiser)
- [VoiceFixer Documentation](https://github.com/haoheliu/voicefixer)
- [PyTorch Audio Processing](https://pytorch.org/audio/)

---

*Last Updated: November 2025*

