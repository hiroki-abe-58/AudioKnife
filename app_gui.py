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

# ===== Mode Definitions =====
# Each mode contains: display_name, models_used, description, best_for, speed
PROCESSING_MODES = {
    "standard": {
        "display_name": "Standard",
        "models": [
            {"name": "Facebook Denoiser", "role": "Noise Reduction", "source": "Meta AI Research"},
            {"name": "VoiceFixer", "role": "Audio Enhancement", "source": "haoheliu"}
        ],
        "description": "2段階処理: まずノイズを除去し、次に音質を向上させます",
        "best_for": "一般的な音声クリーンアップ",
        "speed": "Medium",
        "pipeline": "Denoiser → VoiceFixer (Mode 0)"
    },
    "high_noise": {
        "display_name": "High Noise",
        "models": [
            {"name": "Facebook Denoiser", "role": "Noise Reduction", "source": "Meta AI Research"},
            {"name": "VoiceFixer", "role": "Aggressive Enhancement", "source": "haoheliu"}
        ],
        "description": "強力なノイズ除去モード: VoiceFixerのアグレッシブ設定を使用",
        "best_for": "背景ノイズが大きい録音",
        "speed": "Medium",
        "pipeline": "Denoiser → VoiceFixer (Mode 1)"
    },
    "severely_degraded": {
        "display_name": "Severely Degraded",
        "models": [
            {"name": "Facebook Denoiser", "role": "Noise Reduction", "source": "Meta AI Research"},
            {"name": "VoiceFixer", "role": "Maximum Restoration", "source": "haoheliu"}
        ],
        "description": "最大復元モード: 極度に劣化した音声の修復を試みます",
        "best_for": "品質が非常に低い録音",
        "speed": "Medium",
        "pipeline": "Denoiser → VoiceFixer (Mode 2)"
    },
    "bgm_removal": {
        "display_name": "BGM Removal",
        "models": [
            {"name": "Demucs (htdemucs)", "role": "Source Separation", "source": "Meta AI Research"}
        ],
        "description": "音楽分離AI: 音声とBGMを分離し、ボーカルのみを抽出",
        "best_for": "BGM除去、ポッドキャスト、動画の音声抽出",
        "speed": "Slow",
        "pipeline": "Demucs (Hybrid Transformer)"
    },
    "denoiser_only": {
        "display_name": "Denoiser Only",
        "models": [
            {"name": "Facebook Denoiser", "role": "Noise Reduction", "source": "Meta AI Research"}
        ],
        "description": "シンプルなノイズ除去のみ: 高速で軽量な処理",
        "best_for": "簡単なクリーンアップ、バッチ処理",
        "speed": "Fast",
        "pipeline": "Denoiser Only"
    },
    "resemble_denoise": {
        "display_name": "Resemble Denoise",
        "models": [
            {"name": "Resemble Enhance (Denoiser)", "role": "SE/Noise Separation", "source": "Resemble AI"}
        ],
        "description": "効果音・環境音の分離: 拍手、SE、背景音を除去",
        "best_for": "効果音、拍手、環境ノイズの除去",
        "speed": "Fast",
        "pipeline": "Resemble Denoiser"
    },
    "resemble_enhance": {
        "display_name": "Resemble Enhance",
        "models": [
            {"name": "Resemble Enhance (Denoiser)", "role": "Noise Removal", "source": "Resemble AI"},
            {"name": "Resemble Enhance (Enhancer)", "role": "Quality Boost", "source": "Resemble AI"}
        ],
        "description": "高品質処理: ノイズ除去 + ニューラルネットワークによる音質向上",
        "best_for": "最高品質の音声強化",
        "speed": "Medium",
        "pipeline": "Resemble Denoiser → Enhancer"
    },
    "spleeter_2stems": {
        "display_name": "Spleeter (Vocal)",
        "models": [
            {"name": "Spleeter 2stems", "role": "Vocal/Accompaniment Separation", "source": "Deezer Research"}
        ],
        "description": "音源分離AI: ボーカルと伴奏を分離し、ボーカルのみを抽出",
        "best_for": "カラオケ音源からのボーカル抽出、BGM除去",
        "speed": "Fast",
        "pipeline": "Spleeter (2stems)"
    },
    "spleeter_4stems": {
        "display_name": "Spleeter (4stems)",
        "models": [
            {"name": "Spleeter 4stems", "role": "Multi-track Separation", "source": "Deezer Research"}
        ],
        "description": "4トラック分離: ボーカル/ドラム/ベース/その他に分離",
        "best_for": "楽器ごとの分離が必要な場合",
        "speed": "Medium",
        "pipeline": "Spleeter (4stems)"
    },
    "spleeter_5stems": {
        "display_name": "Spleeter (5stems)",
        "models": [
            {"name": "Spleeter 5stems", "role": "Full Separation", "source": "Deezer Research"}
        ],
        "description": "5トラック分離: ボーカル/ドラム/ベース/ピアノ/その他に分離",
        "best_for": "最も詳細な楽器分離",
        "speed": "Medium",
        "pipeline": "Spleeter (5stems)"
    },
    "mp_senet": {
        "display_name": "MP-SENet (High Quality)",
        "models": [
            {"name": "MP-SENet", "role": "Speech Enhancement", "source": "INTERSPEECH 2023"}
        ],
        "description": "高品質音声強調: magnitude/phaseを並列処理してノイズ除去",
        "best_for": "ノイズの多い録音の高品質クリーンアップ",
        "speed": "Fast",
        "pipeline": "MP-SENet"
    },
    "mossformer2": {
        "display_name": "MossFormer2 (Speaker Separation)",
        "models": [
            {"name": "MossFormer2", "role": "Speech Separation", "source": "Alibaba DAMO"}
        ],
        "description": "話者分離: 複数音声が混在した音源から特定話者を抽出",
        "best_for": "ノイズに混じった音声の抽出、複数話者分離",
        "speed": "Medium",
        "pipeline": "MossFormer2"
    }
}

# Map display names to internal keys
MODE_NAME_MAP = {
    "Standard (Denoiser + VoiceFixer)": "standard",
    "High Noise (Aggressive)": "high_noise",
    "Severely Degraded": "severely_degraded",
    "BGM Removal (Demucs)": "bgm_removal",
    "Denoiser Only": "denoiser_only",
    "Resemble Denoise (SE/Noise removal)": "resemble_denoise",
    "Resemble Enhance (Denoise + Quality)": "resemble_enhance",
    "Spleeter (Vocal Extract)": "spleeter_2stems",
    "Spleeter (4stems)": "spleeter_4stems",
    "Spleeter (5stems)": "spleeter_5stems",
    "MP-SENet (High Quality)": "mp_senet",
    "MossFormer2 (Speaker Separation)": "mossformer2"
}

def get_mode_info_html(mode_name):
    """Generate HTML for mode information display (Light theme)"""
    mode_key = MODE_NAME_MAP.get(mode_name, "resemble_denoise")
    mode = PROCESSING_MODES[mode_key]
    
    # Speed indicator colors
    speed_colors = {"Fast": "#4CAF50", "Medium": "#FF9800", "Slow": "#f44336"}
    speed_color = speed_colors.get(mode["speed"], "#9E9E9E")
    
    models_html = ""
    for i, model in enumerate(mode["models"]):
        arrow = " → " if i < len(mode["models"]) - 1 else ""
        models_html += f"""
        <div style="display: inline-flex; align-items: center; margin: 4px 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: #ffffff; padding: 8px 12px; border-radius: 8px; 
                        font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                <div style="font-weight: 600; color: #ffffff;">{model["name"]}</div>
                <div style="font-size: 11px; color: rgba(255,255,255,0.9);">{model["role"]}</div>
                <div style="font-size: 10px; color: rgba(255,255,255,0.8);">by {model["source"]}</div>
            </div>
            <span style="font-size: 20px; margin: 0 8px; color: #666666;">{arrow}</span>
        </div>
        """
    
    html = f"""
    <div style="background: #f5f5f5; border-radius: 12px; padding: 16px; margin-top: 8px; 
                border: 1px solid #e0e0e0; font-family: system-ui, -apple-system, sans-serif;">
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin: 0; color: #333333; font-size: 16px; font-weight: 600;">
                Processing Pipeline
            </h4>
            <span style="background: {speed_color}; color: #ffffff; padding: 4px 12px; 
                         border-radius: 12px; font-size: 12px; font-weight: 600;">
                {mode["speed"]}
            </span>
        </div>
        
        <div style="display: flex; flex-wrap: wrap; align-items: center; margin-bottom: 16px;">
            {models_html}
        </div>
        
        <div style="background: #ffffff; border-radius: 8px; padding: 12px; margin-bottom: 8px; border: 1px solid #e0e0e0;">
            <div style="color: #666666; font-size: 12px; margin-bottom: 4px; font-weight: 500;">Description</div>
            <div style="color: #333333; font-size: 14px;">{mode["description"]}</div>
        </div>
        
        <div style="background: #ffffff; border-radius: 8px; padding: 12px; border: 1px solid #e0e0e0;">
            <div style="color: #666666; font-size: 12px; margin-bottom: 4px; font-weight: 500;">Best For</div>
            <div style="color: #333333; font-size: 14px;">{mode["best_for"]}</div>
        </div>
    </div>
    """
    return html

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

# Spleeter venv paths to check
SPLEETER_VENV_PATHS = [
    Path.home() / "spleeter_env",
    Path.home() / "spleeter_venv",
    Path.home() / ".spleeter",
]

def find_demucs_venv():
    """Find Demucs virtual environment"""
    for path in DEMUCS_VENV_PATHS:
        if (path / "bin" / "python").exists():
            return path
    return None

def find_spleeter_venv():
    """Find Spleeter virtual environment"""
    for path in SPLEETER_VENV_PATHS:
        if (path / "bin" / "python").exists():
            return path
    return None

DEMUCS_VENV = find_demucs_venv()
SPLEETER_VENV = find_spleeter_venv()


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


def run_spleeter(input_file, output_file, stems="2stems", extract_stem="vocals"):
    """
    Run Spleeter for source separation
    
    Args:
        input_file: Input audio file path
        output_file: Output audio file path
        stems: Model type - "2stems", "4stems", or "5stems"
        extract_stem: Which stem to extract - "vocals", "drums", "bass", "piano", "other"
    
    Returns:
        tuple: (output_file_path, status_message)
    """
    if not SPLEETER_VENV:
        return None, "Spleeter not found. Please install Spleeter first."
    
    spleeter_python = SPLEETER_VENV / "bin" / "python"
    spleeter_cmd = SPLEETER_VENV / "bin" / "spleeter"
    
    if not spleeter_python.exists():
        return None, f"Spleeter Python not found at {spleeter_python}"
    
    temp_output_dir = Path(output_file).parent / "spleeter_temp"
    temp_output_dir.mkdir(exist_ok=True)
    
    # Build spleeter command
    cmd = [
        str(spleeter_cmd), "separate",
        "-p", f"spleeter:{stems}",
        "-o", str(temp_output_dir),
        str(input_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            input_name = Path(input_file).stem
            stem_path = temp_output_dir / input_name / f"{extract_stem}.wav"
            
            if stem_path.exists():
                shutil.copy(stem_path, output_file)
                shutil.rmtree(temp_output_dir)
                return output_file, f"Spleeter ({stems}): OK - Extracted {extract_stem}"
            else:
                # Try to find what was created
                created_dir = temp_output_dir / input_name
                if created_dir.exists():
                    available_stems = list(created_dir.glob("*.wav"))
                    stems_info = ", ".join([s.stem for s in available_stems])
                    return None, f"Spleeter: {extract_stem} not found. Available: {stems_info}"
                return None, f"Spleeter: Output not found at {stem_path}"
        else:
            return None, f"Spleeter failed: {result.stderr[-300:]}"
    except Exception as e:
        return None, f"Spleeter error: {str(e)}"
    finally:
        if temp_output_dir.exists():
            try:
                shutil.rmtree(temp_output_dir)
            except:
                pass


def run_mp_senet(input_file, output_file):
    """
    Run MP-SENet for high-quality speech enhancement
    
    Args:
        input_file: Input audio file path
        output_file: Output audio file path
    
    Returns:
        tuple: (output_file_path, status_message)
    """
    venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
    mp_senet_script = SCRIPT_DIR / "scripts" / "run_mp_senet.py"
    
    if not venv_python.exists():
        return None, "Python venv not found"
    
    if not mp_senet_script.exists():
        return None, "MP-SENet script not found"
    
    cmd = [str(venv_python), str(mp_senet_script), str(input_file), "-o", str(output_file)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            return output_file, "MP-SENet: OK"
        else:
            return None, f"MP-SENet failed: {result.stderr[-300:]}"
    except Exception as e:
        return None, f"MP-SENet error: {str(e)}"


def run_mossformer2(input_file, output_file, speaker_index=0):
    """
    Run MossFormer2 for speaker separation
    
    Args:
        input_file: Input audio file path
        output_file: Output audio file path
        speaker_index: Index of speaker to extract (0-based)
    
    Returns:
        tuple: (output_file_path, status_message)
    """
    venv_python = SCRIPT_DIR / "venv" / "bin" / "python"
    mossformer2_script = SCRIPT_DIR / "scripts" / "run_mossformer2.py"
    
    if not venv_python.exists():
        return None, "Python venv not found"
    
    if not mossformer2_script.exists():
        return None, "MossFormer2 script not found"
    
    cmd = [
        str(venv_python), str(mossformer2_script), 
        str(input_file), 
        "-o", str(output_file),
        "-s", str(speaker_index)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            return output_file, f"MossFormer2: OK - Speaker {speaker_index + 1} extracted"
        else:
            return None, f"MossFormer2 failed: {result.stderr[-300:]}"
    except Exception as e:
        return None, f"MossFormer2 error: {str(e)}"


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
            
            elif mode == "Spleeter (Vocal Extract)":
                progress(0.3, desc="Running Spleeter (2stems)...")
                result, msg = run_spleeter(input_path, output_path, "2stems", "vocals")
                status_messages.append(msg)
            
            elif mode == "Spleeter (4stems)":
                progress(0.3, desc="Running Spleeter (4stems)...")
                result, msg = run_spleeter(input_path, output_path, "4stems", "vocals")
                status_messages.append(msg)
            
            elif mode == "Spleeter (5stems)":
                progress(0.3, desc="Running Spleeter (5stems)...")
                result, msg = run_spleeter(input_path, output_path, "5stems", "vocals")
                status_messages.append(msg)
            
            elif mode == "MP-SENet (High Quality)":
                progress(0.3, desc="Running MP-SENet...")
                result, msg = run_mp_senet(input_path, output_path)
                status_messages.append(msg)
            
            elif mode == "MossFormer2 (Speaker Separation)":
                progress(0.3, desc="Running MossFormer2...")
                result, msg = run_mossformer2(input_path, output_path)
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

def get_features_status_html():
    """Generate HTML for features availability status (Light theme)"""
    features = []
    
    denoiser_available = (CLEARSOUND_DIR / "venv" / "bin" / "python").exists()
    voicefixer_available = (VOICEFIXER_DIR / "venv" / "bin" / "python").exists()
    demucs_available = DEMUCS_VENV is not None
    resemble_available = (SCRIPT_DIR / "scripts" / "run_resemble_enhance.py").exists()
    spleeter_available = SPLEETER_VENV is not None
    mp_senet_available = (SCRIPT_DIR / "scripts" / "run_mp_senet.py").exists()
    mossformer2_available = (SCRIPT_DIR / "scripts" / "run_mossformer2.py").exists()
    
    features = [
        ("Facebook Denoiser", denoiser_available, "Meta AI Research"),
        ("VoiceFixer", voicefixer_available, "haoheliu"),
        ("Demucs", demucs_available, "Meta AI Research"),
        ("Resemble Enhance", resemble_available, "Resemble AI"),
        ("Spleeter", spleeter_available, "Deezer Research"),
        ("MP-SENet", mp_senet_available, "INTERSPEECH 2023"),
        ("MossFormer2", mossformer2_available, "Alibaba DAMO"),
    ]
    
    html = '<div style="display: flex; flex-wrap: wrap; gap: 8px;">'
    for name, available, source in features:
        if available:
            bg_color = "#e8f5e9"
            border_color = "#4CAF50"
            icon_color = "#2e7d32"
            icon = "check_circle"
        else:
            bg_color = "#f5f5f5"
            border_color = "#bdbdbd"
            icon_color = "#757575"
            icon = "cancel"
        
        html += f"""
        <div style="display: flex; align-items: center; background: {bg_color}; 
                    border: 1px solid {border_color}; border-radius: 8px; padding: 6px 10px;">
            <span class="material-icons" style="font-size: 16px; color: {icon_color}; margin-right: 6px;">{icon}</span>
            <div>
                <div style="font-size: 12px; font-weight: 600; color: #333333;">{name}</div>
                <div style="font-size: 10px; color: #666666;">{source}</div>
            </div>
        </div>
        """
    html += '</div>'
    return html


def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(title="AudioKnife") as demo:
        # Header with embedded CSS (Light theme)
        gr.HTML("""
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #ffffff;
                padding: 24px;
                border-radius: 16px;
                margin-bottom: 20px;
                text-align: center;
            }
            .main-header h1 {
                margin: 0;
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
            }
            .main-header p {
                margin: 8px 0 0 0;
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
            }
            .section-title {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 12px;
                font-weight: 600;
                color: #333333;
            }
        </style>
        <div class="main-header">
            <h1>AudioKnife</h1>
            <p>AI-Powered Audio Enhancement & Noise Removal</p>
        </div>
        """)
        
        with gr.Row():
            # Left Column - Input & Controls
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="section-title">
                    <span class="material-icons" style="color: #667eea;">upload_file</span>
                    <span style="color: #333333;">Input</span>
                </div>
                """)
                audio_input = gr.Audio(
                    label="Upload Audio File",
                    type="filepath",
                    sources=["upload", "microphone"]
                )
                
                gr.HTML("""
                <div class="section-title" style="margin-top: 20px;">
                    <span class="material-icons" style="color: #667eea;">tune</span>
                    <span style="color: #333333;">Processing Mode</span>
                </div>
                """)
                mode_select = gr.Radio(
                    choices=[
                        "Standard (Denoiser + VoiceFixer)",
                        "High Noise (Aggressive)",
                        "Severely Degraded",
                        "BGM Removal (Demucs)",
                        "Denoiser Only",
                        "Resemble Denoise (SE/Noise removal)",
                        "Resemble Enhance (Denoise + Quality)",
                        "Spleeter (Vocal Extract)",
                        "Spleeter (4stems)",
                        "Spleeter (5stems)",
                        "MP-SENet (High Quality)",
                        "MossFormer2 (Speaker Separation)"
                    ],
                    value="Resemble Denoise (SE/Noise removal)",
                    label="",
                    info=""
                )
                
                # Dynamic mode info display
                mode_info_display = gr.HTML(
                    value=get_mode_info_html("Resemble Denoise (SE/Noise removal)"),
                    label=""
                )
                
                # Process button
                process_btn = gr.Button(
                    "Process Audio",
                    variant="primary",
                    size="lg"
                )
                
                # Features status
                gr.HTML("""
                <div class="section-title" style="margin-top: 20px;">
                    <span class="material-icons" style="color: #667eea;">hub</span>
                    <span style="color: #333333;">Available AI Models</span>
                </div>
                """)
                gr.HTML(get_features_status_html())
            
            # Right Column - Output
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="section-title">
                    <span class="material-icons" style="color: #667eea;">audio_file</span>
                    <span style="color: #333333;">Output</span>
                </div>
                """)
                audio_output = gr.Audio(
                    label="Processed Audio",
                    type="filepath"
                )
                
                gr.HTML("""
                <div class="section-title" style="margin-top: 20px;">
                    <span class="material-icons" style="color: #667eea;">terminal</span>
                    <span style="color: #333333;">Processing Log</span>
                </div>
                """)
                status_output = gr.Textbox(
                    label="",
                    lines=12,
                    max_lines=18,
                    interactive=False,
                    placeholder="Processing status will appear here..."
                )
        
        # Model Reference Section
        with gr.Accordion("AI Models Reference", open=False):
            gr.HTML("""
            <div style="padding: 16px; background: #ffffff; border-radius: 8px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 14px; background: #ffffff;">
                    <thead>
                        <tr style="background: #f5f5f5;">
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #667eea; color: #333333; font-weight: 600;">Model</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #667eea; color: #333333; font-weight: 600;">Source</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #667eea; color: #333333; font-weight: 600;">Function</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #667eea; color: #333333; font-weight: 600;">Used In Modes</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="background: #ffffff;">
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333333;">
                                <strong>Facebook Denoiser</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">Meta AI Research</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Real-time speech enhancement in waveform domain
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Standard, High Noise, Severely Degraded, Denoiser Only
                            </td>
                        </tr>
                        <tr style="background: #fafafa;">
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333333;">
                                <strong>VoiceFixer</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">haoheliu (GitHub)</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Audio restoration and quality enhancement
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Standard, High Noise, Severely Degraded
                            </td>
                        </tr>
                        <tr style="background: #ffffff;">
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333333;">
                                <strong>Demucs (htdemucs)</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">Meta AI Research</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Hybrid Transformer for music source separation
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                BGM Removal
                            </td>
                        </tr>
                        <tr style="background: #fafafa;">
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333333;">
                                <strong>Resemble Enhance</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">Resemble AI</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                SE/noise separation + neural audio enhancement
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Resemble Denoise, Resemble Enhance
                            </td>
                        </tr>
                        <tr style="background: #ffffff;">
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333333;">
                                <strong>Spleeter</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">Deezer Research</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Fast music source separation (2/4/5 stems)
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Spleeter (Vocal), Spleeter (4stems), Spleeter (5stems)
                            </td>
                        </tr>
                        <tr style="background: #fafafa;">
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333333;">
                                <strong>MP-SENet</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">INTERSPEECH 2023</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                High-quality speech enhancement (magnitude/phase parallel processing, PESQ 3.50)
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                MP-SENet (High Quality)
                            </td>
                        </tr>
                        <tr style="background: #ffffff;">
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #333333;">
                                <strong>MossFormer2</strong>
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">Alibaba DAMO</td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                Speaker separation (Transformer + RNN-Free recurrent network)
                            </td>
                            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #666666;">
                                MossFormer2 (Speaker Separation)
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """)
        
        # Event handlers
        # Update mode info when mode is selected
        mode_select.change(
            fn=get_mode_info_html,
            inputs=[mode_select],
            outputs=[mode_info_display]
        )
        
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
    print(f"Spleeter venv: {SPLEETER_VENV}")
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

