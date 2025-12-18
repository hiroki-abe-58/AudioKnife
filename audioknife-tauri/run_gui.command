#!/bin/bash
# AudioKnife - Apple Silicon Optimized Audio Processor
# Double-click to launch the application

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "AudioKnife - Starting..."
echo "========================================"

# Check if app is already built
APP_PATH="$SCRIPT_DIR/src-tauri/target/release/bundle/macos/AudioKnife.app"

if [ -d "$APP_PATH" ]; then
    echo "Launching AudioKnife.app..."
    open "$APP_PATH"
else
    echo "Built app not found. Starting in development mode..."
    echo ""
    
    # Check dependencies
    if ! command -v npm &> /dev/null; then
        echo "Error: npm is not installed"
        echo "Please install Node.js from https://nodejs.org/"
        read -p "Press Enter to close..."
        exit 1
    fi
    
    if ! command -v cargo &> /dev/null; then
        echo "Error: Rust/Cargo is not installed"
        echo "Please install Rust from https://rustup.rs/"
        read -p "Press Enter to close..."
        exit 1
    fi
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install
    fi
    
    # Start development server
    echo "Starting Tauri development server..."
    echo "(This may take a moment on first run)"
    echo ""
    npm run tauri dev
fi
