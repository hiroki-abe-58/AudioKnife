#!/bin/bash
# Build AudioKnife for release (Universal Binary for macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "AudioKnife Release Build"
echo "========================================"

# Check requirements
echo "Checking requirements..."

if ! command -v cargo &> /dev/null; then
    echo "Error: Rust/Cargo not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm not installed"
    exit 1
fi

# Install Rust targets for Universal Binary
echo "Installing Rust targets..."
rustup target add aarch64-apple-darwin x86_64-apple-darwin 2>/dev/null || true

# Install npm dependencies
echo "Installing npm dependencies..."
npm install

# Build for Apple Silicon (arm64)
echo ""
echo "Building for Apple Silicon (arm64)..."
npm run tauri build -- --target aarch64-apple-darwin

# Build for Intel (x86_64) - Optional, uncomment if needed
# echo ""
# echo "Building for Intel (x86_64)..."
# npm run tauri build -- --target x86_64-apple-darwin

# Create Universal Binary (if both architectures built)
# echo ""
# echo "Creating Universal Binary..."
# lipo -create \
#     target/aarch64-apple-darwin/release/bundle/macos/AudioKnife.app/Contents/MacOS/AudioKnife \
#     target/x86_64-apple-darwin/release/bundle/macos/AudioKnife.app/Contents/MacOS/AudioKnife \
#     -output target/universal/AudioKnife

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Output location:"
echo "  src-tauri/target/aarch64-apple-darwin/release/bundle/"
echo ""
echo "Files:"
ls -la src-tauri/target/aarch64-apple-darwin/release/bundle/macos/ 2>/dev/null || echo "  (check src-tauri/target/release/bundle/)"

echo ""
echo "To sign and notarize for distribution:"
echo "  1. Set APPLE_SIGNING_IDENTITY environment variable"
echo "  2. Set APPLE_ID and APPLE_PASSWORD for notarization"
echo "  3. Run: npm run tauri build -- --target aarch64-apple-darwin"
