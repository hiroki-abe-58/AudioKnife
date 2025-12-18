#!/usr/bin/env python3
"""
AudioKnife Python AI Backend
FastAPI server for AI-powered audio processing
Optimized for Apple Silicon with MPS support
"""

import os
import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
PARENT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PARENT_DIR))

# ===== App Configuration =====
app = FastAPI(
    title="AudioKnife AI Backend",
    description="AI-powered audio processing server optimized for Apple Silicon",
    version="0.1.0"
)

# CORS middleware for Tauri app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Request/Response Models =====

class ProcessRequest(BaseModel):
    input_path: str
    output_path: Optional[str] = None
    mode: str = "resemble_denoise"

class ProcessResponse(BaseModel):
    success: bool
    output_path: Optional[str] = None
    message: str
    processing_time: Optional[float] = None

class StatusResponse(BaseModel):
    status: str
    available_modes: List[str]
    mps_available: bool
    cuda_available: bool

class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float
    message: str

# ===== Global State =====
jobs = {}

# ===== Helper Functions =====

def check_mps_available():
    """Check if Apple Silicon MPS is available"""
    try:
        import torch
        return torch.backends.mps.is_available()
    except:
        return False

def check_cuda_available():
    """Check if CUDA is available"""
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False

def get_device():
    """Get the best available device for processing"""
    if check_mps_available():
        return "mps"
    elif check_cuda_available():
        return "cuda"
    else:
        return "cpu"

# ===== Processing Functions =====

async def process_resemble_denoise(input_path: str, output_path: str) -> ProcessResponse:
    """Process with Resemble Enhance - Denoise only"""
    try:
        from processors.resemble_processor import ResembleProcessor
        processor = ResembleProcessor()
        result = await processor.denoise(input_path, output_path)
        return ProcessResponse(
            success=True,
            output_path=result,
            message="Resemble Denoise completed successfully"
        )
    except Exception as e:
        return ProcessResponse(
            success=False,
            message=f"Resemble Denoise failed: {str(e)}"
        )

async def process_resemble_enhance(input_path: str, output_path: str) -> ProcessResponse:
    """Process with Resemble Enhance - Denoise + Enhance"""
    try:
        from processors.resemble_processor import ResembleProcessor
        processor = ResembleProcessor()
        result = await processor.enhance(input_path, output_path)
        return ProcessResponse(
            success=True,
            output_path=result,
            message="Resemble Enhance completed successfully"
        )
    except Exception as e:
        return ProcessResponse(
            success=False,
            message=f"Resemble Enhance failed: {str(e)}"
        )

async def process_demucs(input_path: str, output_path: str) -> ProcessResponse:
    """Process with Demucs for BGM removal"""
    try:
        from processors.demucs_processor import DemucsProcessor
        processor = DemucsProcessor()
        result = await processor.separate(input_path, output_path)
        return ProcessResponse(
            success=True,
            output_path=result,
            message="Demucs BGM removal completed successfully"
        )
    except Exception as e:
        return ProcessResponse(
            success=False,
            message=f"Demucs failed: {str(e)}"
        )

async def process_spleeter(input_path: str, output_path: str, stems: str = "2stems") -> ProcessResponse:
    """Process with Spleeter for vocal extraction"""
    try:
        from processors.spleeter_processor import SpleeterProcessor
        processor = SpleeterProcessor()
        result = await processor.separate(input_path, output_path, stems)
        return ProcessResponse(
            success=True,
            output_path=result,
            message=f"Spleeter {stems} completed successfully"
        )
    except Exception as e:
        return ProcessResponse(
            success=False,
            message=f"Spleeter failed: {str(e)}"
        )

# ===== API Endpoints =====

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "AudioKnife AI Backend",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get server status and available processing modes"""
    return StatusResponse(
        status="running",
        available_modes=[
            "resemble_denoise",
            "resemble_enhance",
            "demucs",
            "spleeter_2stems",
            "spleeter_4stems",
            "spleeter_5stems",
            "mp_senet",
            "mossformer2"
        ],
        mps_available=check_mps_available(),
        cuda_available=check_cuda_available()
    )

@app.post("/process", response_model=ProcessResponse)
async def process_audio(request: ProcessRequest):
    """Process audio file with specified AI model"""
    start_time = datetime.now()
    
    # Validate input
    if not os.path.exists(request.input_path):
        raise HTTPException(status_code=404, detail="Input file not found")
    
    # Set output path if not provided
    output_path = request.output_path
    if not output_path:
        input_p = Path(request.input_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(input_p.parent / f"{timestamp}_{input_p.stem}_processed.wav")
    
    # Process based on mode
    mode = request.mode.lower()
    
    if mode == "resemble_denoise":
        result = await process_resemble_denoise(request.input_path, output_path)
    elif mode == "resemble_enhance":
        result = await process_resemble_enhance(request.input_path, output_path)
    elif mode == "demucs":
        result = await process_demucs(request.input_path, output_path)
    elif mode in ["spleeter_2stems", "spleeter_4stems", "spleeter_5stems"]:
        stems = mode.replace("spleeter_", "")
        result = await process_spleeter(request.input_path, output_path, stems)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown processing mode: {mode}")
    
    # Add processing time
    result.processing_time = (datetime.now() - start_time).total_seconds()
    
    return result

@app.get("/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of a processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "device": get_device()}

# ===== Main =====

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AudioKnife AI Backend")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    print("=" * 50)
    print("AudioKnife AI Backend")
    print("=" * 50)
    print(f"Device: {get_device()}")
    print(f"MPS Available: {check_mps_available()}")
    print(f"CUDA Available: {check_cuda_available()}")
    print("=" * 50)
    
    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
