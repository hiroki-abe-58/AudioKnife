# Contributing to AudioCleaner

Thank you for your interest in contributing to AudioCleaner! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions with the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Audio file format and characteristics (if relevant)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any relevant examples or references

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and modular

### Testing

Before submitting a PR:
- Test with various audio formats (WAV, MP3, FLAC)
- Test with different file sizes
- Test all processing modes
- Verify error handling

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/AudioCleaner.git
cd AudioCleaner

# Install in development mode
./install.sh

# Activate virtual environment
source venv/bin/activate

# Run tests (when available)
# pytest tests/
```

## Areas for Contribution

### High Priority
- Cross-platform support (Linux, Windows)
- Batch processing mode
- GUI interface
- More audio format support
- Performance optimizations

### Medium Priority
- Progress bars for long files
- Audio quality metrics
- Configuration file support
- Docker container

### Documentation
- More usage examples
- Video tutorials
- Troubleshooting guide
- Performance benchmarks

## Questions?

Feel free to open an issue with the "question" label.

Thank you for contributing! 🎵

