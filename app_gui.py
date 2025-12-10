#!/usr/bin/env python3
"""
AudioCleaner Pro - GUI Version
Gradio-based web interface for audio enhancement and noise removal
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import gradio as gr

# ===== Configuration =====
SCRIPT_DIR = Path(__file__).parent.resolve()
VOICEFIXER_DIR = Path.home() / "voicefixer_app"
CLEARSOUND_DIR = Path.home() / "clearSound"

# Demucs venv paths to check
DEMUCS_VENV_PATHS = [
    Path.home() / "demucs_venv310",
    Path.home() / "demucs_venv",
    Path.home() / ".demucs",
]

def find_demucs_venv():
    """Find Demucs virtual environment"""
    for path in DEMUCS_VENV_PATHS:
        if (path / "bin" / "python").exists():
            return path
    return None

DEMUCS_VENV = find_demucs_venv()


# ===== Processing Functions =====

def run_denoiser(input_file, output_file):
    """Run Facebook Denoiser for noise reduction"""
    denoiser_venv = CLEARSOUND_DIR / "venv" / "bin" / "python"
    denoiser_script = CLEARSOUND_DIR / "run_clearSound.py"
    
    if not denoiser_venv.exists() or not denoiser_script.exists():
        return None, "Denoiser not found. Please install clearSound first."
    
    cmd = [str(denoiser_venv), str(denoiser_script), str(input_file), "-o", str(output_file), "-q", "high"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(CLEARSOUND_DIR))
        if result.returncode == 0:
            return output_file, "Denoiser: OK"
        else:
            return None, f"Denoiser failed: {result.stderr[:200]}"
    except Exception as e:
        return None, f"Denoiser error: {str(e)}"


def run_voicefixer(input_file, output_file, mode=0):
    """Run VoiceFixer for audio enhancement"""
    venv_python = VOICEFIXER_DIR / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        return None, "VoiceFixer not found. Please install VoiceFixer first."
    
    cmd = [str(venv_python), "-c", f"""
import sys
sys.path.insert(0, '{VOICEFIXER_DIR}')
sys.path.insert(0, '{VOICEFIXER_DIR}/voicefixer')

from voicefixer import VoiceFixer
vf = VoiceFixer()
vf.restore('{input_file}', '{output_file}', cuda=False, mode={mode})
print('OK')
"""]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(VOICEFIXER_DIR))
        if result.returncode == 0:
            return output_file, "VoiceFixer: OK"
        else:
            return None, f"VoiceFixer failed: {result.stderr[:200]}"
    except Exception as e:
        return None, f"VoiceFixer error: {str(e)}"


def run_demucs(input_file, output_file):
    """Run Demucs for BGM removal / vocal extraction"""
    if not DEMUCS_VENV:
        return None, "Demucs not found. Please install Demucs first."
    
    demucs_python = DEMUCS_VENV / "bin" / "python"
    
    if not demucs_python.exists():
        return None, f"Demucs Python not found at {demucs_python}"
    
    temp_output_dir = Path(output_file).parent / "demucs_temp"
    temp_output_dir.mkdir(exist_ok=True)
    
    cmd = [
        str(demucs_python), "-m", "demucs.separate",
        "-n", "htdemucs",
        "--two-stems=vocals",
        "-d", "cpu",
        "-o", str(temp_output_dir),
        str(input_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            input_name = Path(input_file).stem
            vocals_path = temp_output_dir / "htdemucs" / input_name / "vocals.wav"
            
            if vocals_path.exists():
                shutil.copy(vocals_path, output_file)
                shutil.rmtree(temp_output_dir)
                return output_file, "Demucs: OK"
            else:
                return None, "Demucs: Vocals file not found"
        else:
            return None, f"Demucs failed: {result.stderr[-300:]}"
    except Exception as e:
        return None, f"Demucs error: {str(e)}"
    finally:
        if temp_output_dir.exists():
            try:
                shutil.rmtree(temp_output_dir)
            except:
                pass


def run_resemble_enhance(input_file, output_file, mode="denoise"):
    """Run Resemble Enhance for SE/noise removal"""
    venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
    resemble_script = SCRIPT_DIR / "scripts" / "run_resemble_enhance.py"
    
    if not venv_python.exists():
        return None, "Python venv not found"
    
    if not resemble_script.exists():
        return None, "Resemble Enhance script not found"
    
    cmd = [str(venv_python), str(resemble_script), str(input_file), "-o", str(output_file), "-m", mode]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            return output_file, f"Resemble Enhance ({mode}): OK"
        else:
            return None, f"Resemble Enhance failed: {result.stderr[-300:]}"
    except Exception as e:
        return None, f"Resemble Enhance error: {str(e)}"


# ===== Main Processing Function =====

def process_audio(audio_file, mode, progress=gr.Progress()):
    """
    Main audio processing function
    
    Args:
        audio_file: Input audio file path
        mode: Processing mode
        progress: Gradio progress tracker
    
    Returns:
        tuple: (output_file_path, status_message)
    """
    if audio_file is None:
        return None, "Please upload an audio file first."
    
    input_path = Path(audio_file)
    
    # Create output filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_name = f"{timestamp}__{input_path.stem}_cleaned.wav"
    output_path = input_path.parent / output_name
    
    status_messages = []
    status_messages.append(f"Input: {input_path.name}")
    status_messages.append(f"Mode: {mode}")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_file = temp_path / "temp_processed.wav"
            
            progress(0.1, desc="Starting processing...")
            
            if mode == "Standard (Denoiser + VoiceFixer)":
                # Step 1: Denoiser
                progress(0.2, desc="Running Denoiser...")
                result, msg = run_denoiser(input_path, temp_file)
                status_messages.append(msg)
                
                if result:
                    current_file = temp_file
                else:
                    current_file = input_path
                
                # Step 2: VoiceFixer
                progress(0.6, desc="Running VoiceFixer...")
                result, msg = run_voicefixer(current_file, output_path, mode=0)
                status_messages.append(msg)
                
                if not result and current_file != input_path:
                    shutil.copy(current_file, output_path)
                    status_messages.append("Saved Denoiser result only")
            
            elif mode == "High Noise (Aggressive)":
                progress(0.2, desc="Running Denoiser...")
                result, msg = run_denoiser(input_path, temp_file)
                status_messages.append(msg)
                
                current_file = temp_file if result else input_path
                
                progress(0.6, desc="Running VoiceFixer (Mode 1)...")
                result, msg = run_voicefixer(current_file, output_path, mode=1)
                status_messages.append(msg)
                
                if not result and current_file != input_path:
                    shutil.copy(current_file, output_path)
            
            elif mode == "Severely Degraded":
                progress(0.2, desc="Running Denoiser...")
                result, msg = run_denoiser(input_path, temp_file)
                status_messages.append(msg)
                
                current_file = temp_file if result else input_path
                
                progress(0.6, desc="Running VoiceFixer (Mode 2)...")
                result, msg = run_voicefixer(current_file, output_path, mode=2)
                status_messages.append(msg)
                
                if not result and current_file != input_path:
                    shutil.copy(current_file, output_path)
            
            elif mode == "BGM Removal (Demucs)":
                progress(0.3, desc="Running Demucs (this may take a while)...")
                result, msg = run_demucs(input_path, output_path)
                status_messages.append(msg)
            
            elif mode == "Denoiser Only":
                progress(0.3, desc="Running Denoiser...")
                result, msg = run_denoiser(input_path, output_path)
                status_messages.append(msg)
            
            elif mode == "Resemble Denoise (SE/Noise removal)":
                progress(0.3, desc="Running Resemble Enhance (Denoise)...")
                result, msg = run_resemble_enhance(input_path, output_path, "denoise")
                status_messages.append(msg)
            
            elif mode == "Resemble Enhance (Denoise + Quality)":
                progress(0.3, desc="Running Resemble Enhance (Full)...")
                result, msg = run_resemble_enhance(input_path, output_path, "enhance")
                status_messages.append(msg)
            
            else:
                return None, f"Unknown mode: {mode}"
            
            progress(0.9, desc="Finalizing...")
            
            if output_path.exists():
                progress(1.0, desc="Complete!")
                status_messages.append(f"\nOutput: {output_path.name}")
                status_messages.append(f"Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
                return str(output_path), "\n".join(status_messages)
            else:
                return None, "\n".join(status_messages) + "\n\nProcessing failed - no output file generated"
    
    except Exception as e:
        import traceback
        return None, f"Error: {str(e)}\n\n{traceback.format_exc()}"


# ===== Gradio Interface =====

def create_interface():
    """Create Gradio interface"""
    
    # Check available features
    features_status = []
    
    if (CLEARSOUND_DIR / "venv" / "bin" / "python").exists():
        features_status.append("- Denoiser: Available")
    else:
        features_status.append("- Denoiser: Not installed")
    
    if (VOICEFIXER_DIR / "venv" / "bin" / "python").exists():
        features_status.append("- VoiceFixer: Available")
    else:
        features_status.append("- VoiceFixer: Not installed")
    
    if DEMUCS_VENV:
        features_status.append(f"- Demucs: Available ({DEMUCS_VENV})")
    else:
        features_status.append("- Demucs: Not installed")
    
    if (SCRIPT_DIR / "scripts" / "run_resemble_enhance.py").exists():
        features_status.append("- Resemble Enhance: Available")
    else:
        features_status.append("- Resemble Enhance: Not installed")
    
    features_text = "\n".join(features_status)
    
    with gr.Blocks(title="AudioCleaner Pro") as demo:
        gr.HTML("""
            <div class="main-title">
                <h1>AudioCleaner Pro</h1>
            </div>
            <div class="subtitle">
                AI-Powered Audio Enhancement & Noise Removal
            </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Input section
                gr.Markdown("### Input")
                audio_input = gr.Audio(
                    label="Upload Audio File",
                    type="filepath",
                    sources=["upload", "microphone"]
                )
                
                # Mode selection
                gr.Markdown("### Processing Mode")
                mode_select = gr.Radio(
                    choices=[
                        "Standard (Denoiser + VoiceFixer)",
                        "High Noise (Aggressive)",
                        "Severely Degraded",
                        "BGM Removal (Demucs)",
                        "Denoiser Only",
                        "Resemble Denoise (SE/Noise removal)",
                        "Resemble Enhance (Denoise + Quality)"
                    ],
                    value="Resemble Denoise (SE/Noise removal)",
                    label="Select Mode",
                    info="Choose the processing mode based on your audio"
                )
                
                # Process button
                process_btn = gr.Button(
                    "Process Audio",
                    variant="primary",
                    size="lg"
                )
                
                # Features status
                with gr.Accordion("Available Features", open=False):
                    gr.Markdown(f"```\n{features_text}\n```")
            
            with gr.Column(scale=1):
                # Output section
                gr.Markdown("### Output")
                audio_output = gr.Audio(
                    label="Processed Audio",
                    type="filepath"
                )
                
                # Status
                status_output = gr.Textbox(
                    label="Processing Status",
                    lines=10,
                    max_lines=15,
                    interactive=False
                )
        
        # Mode descriptions
        gr.Markdown("""
        ### Mode Descriptions
        
        | Mode | Description | Best For |
        |------|-------------|----------|
        | **Standard** | Denoiser + VoiceFixer | General audio cleanup |
        | **High Noise** | Aggressive noise reduction | Recordings with significant background noise |
        | **Severely Degraded** | Maximum restoration | Very poor quality recordings |
        | **BGM Removal** | Demucs vocal extraction | Music/BGM removal, podcasts |
        | **Denoiser Only** | Basic noise reduction | Quick cleanup |
        | **Resemble Denoise** | SE/Noise removal (Fast) | Sound effects, applause, environmental noise |
        | **Resemble Enhance** | Denoise + Quality boost | High-quality enhancement |
        """)
        
        # Event handlers
        process_btn.click(
            fn=process_audio,
            inputs=[audio_input, mode_select],
            outputs=[audio_output, status_output],
            show_progress=True
        )
    
    return demo


# ===== Main =====

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AudioCleaner Pro - GUI")
    parser.add_argument("--port", type=int, default=7860, help="Port to run on")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--server-name", default="127.0.0.1", help="Server name")
    args = parser.parse_args()
    
    print("=" * 50)
    print("AudioCleaner Pro - GUI Version")
    print("=" * 50)
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Demucs venv: {DEMUCS_VENV}")
    print(f"VoiceFixer: {VOICEFIXER_DIR}")
    print(f"ClearSound: {CLEARSOUND_DIR}")
    print("=" * 50)
    
    demo = create_interface()
    demo.launch(
        server_name=args.server_name,
        server_port=args.port,
        share=args.share,
        show_error=True
    )

