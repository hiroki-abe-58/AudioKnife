#!/bin/bash
# Start AudioKnife Python AI Backend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/python-backend"

echo "========================================"
echo "AudioKnife AI Backend"
echo "========================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check PyTorch and MPS
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'MPS Available: {torch.backends.mps.is_available()}')" 2>/dev/null || {
    echo "Warning: PyTorch not found or MPS not available"
}

# Start server
cd "$BACKEND_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting server on http://127.0.0.1:8765"
python server.py --host 127.0.0.1 --port 8765
