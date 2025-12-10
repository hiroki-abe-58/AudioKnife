#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    AudioCleaner PRO v1.2             ║${NC}"
echo -e "${CYAN}║    AI-Powered Audio Enhancement      ║${NC}"
echo -e "${CYAN}║    + SE/Noise Removal (Resemble)     ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Pythonスクリプトを直接埋め込み
cat > /tmp/audio_cleaner_pro.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

def run_denoiser(input_file, output_file, denoiser_dir):
    print("\n" + "="*50)
    print("Step 1: Denoiser - Noise Reduction")
    print("="*50)
    
    # Check for clearSound installation
    clearSound_dir = Path.home() / "clearSound"
    denoiser_venv = clearSound_dir / "venv" / "bin" / "python"
    denoiser_script = clearSound_dir / "run_clearSound.py"
    
    if not denoiser_venv.exists() or not denoiser_script.exists():
        print(f"[SKIP] Denoiser not found at {clearSound_dir}")
        print(f"  Looking for: {denoiser_venv}")
        print(f"  And: {denoiser_script}")
        return None
    
    cmd = [str(denoiser_venv), str(denoiser_script), input_file, "-o", output_file, "-q", "high"]
    
    try:
        print("Processing...")
        print(f"[DEBUG] Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(clearSound_dir))
        if result.returncode == 0:
            print("[SUCCESS] Noise reduction complete!")
            return output_file
        else:
            print(f"[ERROR] Denoiser failed (exit code: {result.returncode})")
            if result.stdout:
                print(f"[STDOUT]\n{result.stdout}")
            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_audiosep(input_file, output_file, script_dir, text_query="human speech"):
    print("\n" + "="*50)
    print("Step 2: AudioSep - SE Removal (Text-guided)")
    print("="*50)
    print(f"Query: '{text_query}'")
    
    venv_python = script_dir / "venv" / "bin" / "python"
    audiosep_script = script_dir / "scripts" / "run_audiosep.py"
    
    if not venv_python.exists() or not audiosep_script.exists():
        print("[SKIP] AudioSep not found")
        return None
    
    cmd = [str(venv_python), str(audiosep_script), input_file, "-o", output_file, "-q", text_query]
    
    try:
        print("Processing...")
        print(f"[DEBUG] Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(script_dir))
        if result.returncode == 0:
            print("[SUCCESS] SE removal complete!")
            return output_file
        else:
            print(f"[ERROR] AudioSep failed (exit code: {result.returncode})")
            if result.stdout:
                print(f"[STDOUT]\n{result.stdout}")
            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_sepformer(input_file, output_file, script_dir):
    print("\n" + "="*50)
    print("Step 3: SepFormer-DNS - Audio Enhancement")
    print("="*50)
    
    venv_python = script_dir / "venv" / "bin" / "python"
    sepformer_script = script_dir / "scripts" / "run_sepformer.py"
    
    if not venv_python.exists() or not sepformer_script.exists():
        print("[SKIP] SepFormer-DNS not found")
        return None
    
    cmd = [str(venv_python), str(sepformer_script), input_file, "-o", output_file]
    
    try:
        print("Processing...")
        print(f"[DEBUG] Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(script_dir))
        if result.returncode == 0:
            print("[SUCCESS] Enhancement complete!")
            return output_file
        else:
            print(f"[ERROR] SepFormer failed (exit code: {result.returncode})")
            if result.stdout:
                print(f"[STDOUT]\n{result.stdout}")
            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_demucs(input_file, output_file, demucs_venv):
    print("\n" + "="*50)
    print("Step 1: Demucs - BGM Removal")
    print("="*50)
    
    # Check for Demucs installation
    demucs_venv_path = Path(demucs_venv)
    demucs_python = demucs_venv_path / "bin" / "python"
    
    if not demucs_python.exists():
        print(f"[ERROR] Demucs Python not found at {demucs_python}")
        print(f"[INFO] Please ensure Demucs is installed:")
        print(f"       python3.10 -m venv ~/demucs_venv310")
        print(f"       source ~/demucs_venv310/bin/activate")
        print(f"       pip install demucs")
        return None
    
    # Create temporary output directory
    temp_output_dir = Path(output_file).parent / "demucs_temp"
    temp_output_dir.mkdir(exist_ok=True)
    print(f"[INFO] Temp output dir: {temp_output_dir}")
    
    # Use CPU only for stability (MPS can have issues with some operations)
    device = "cpu"
    
    cmd = [
        str(demucs_python), "-m", "demucs.separate",
        "-n", "htdemucs",
        "--two-stems=vocals",
        "-d", device,
        "-o", str(temp_output_dir),
        input_file
    ]
    
    print(f"[INFO] Command: {' '.join(cmd)}")
    print(f"Processing with Demucs using {device.upper()}...")
    print("[INFO] This may take a few minutes depending on audio length...")
    sys.stdout.flush()
    
    try:
        # Don't capture output so progress bar is visible
        result = subprocess.run(cmd, text=True)
        
        if result.returncode == 0:
            # Find the vocals.wav output
            input_name = Path(input_file).stem
            vocals_path = temp_output_dir / "htdemucs" / input_name / "vocals.wav"
            
            print(f"[INFO] Looking for vocals at: {vocals_path}")
            
            if vocals_path.exists():
                # Copy to output location
                shutil.copy(vocals_path, output_file)
                # Cleanup
                shutil.rmtree(temp_output_dir)
                print("[SUCCESS] BGM removal complete!")
                return output_file
            else:
                print(f"[ERROR] Vocals file not found: {vocals_path}")
                # List what's in the temp dir for debugging
                print("[DEBUG] Contents of temp directory:")
                for p in temp_output_dir.rglob("*"):
                    print(f"  {p}")
                return None
        else:
            print(f"[ERROR] Demucs failed (exit code: {result.returncode})")
            return None
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Cleanup temp directory if it still exists
        if temp_output_dir.exists():
            try:
                shutil.rmtree(temp_output_dir)
            except:
                pass

def run_resemble_enhance(input_file, output_file, script_dir, mode="denoise"):
    """Resemble Enhanceでノイズ除去/音質向上"""
    print("\n" + "="*50)
    print("Resemble Enhance - SE/Noise Removal")
    print("="*50)
    mode_names = {'denoise': 'Denoise Only (Fast)', 'enhance': 'Denoise + Enhance (High Quality)'}
    print(f"Mode: {mode_names.get(mode, mode)}")
    
    venv_python = script_dir / "venv" / "bin" / "python"
    resemble_script = script_dir / "scripts" / "run_resemble_enhance.py"
    
    if not venv_python.exists():
        print("[ERROR] Python venv not found")
        print(f"Expected path: {venv_python}")
        return False
    
    if not resemble_script.exists():
        print("[ERROR] Resemble Enhance script not found")
        print(f"Expected path: {resemble_script}")
        return False
    
    cmd = [str(venv_python), str(resemble_script), input_file, "-o", output_file, "-m", mode]
    
    try:
        print("Processing... (This may take a while)")
        print(f"[DEBUG] Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False, text=True, cwd=str(script_dir))
        if result.returncode == 0:
            print("[SUCCESS] Resemble Enhance complete!")
            return True
        else:
            print(f"[ERROR] Resemble Enhance failed (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_voicefixer_direct(input_file, output_file, voicefixer_dir, mode=0):
    print("\n" + "="*50)
    print("Step: VoiceFixer - Audio Enhancement")
    print("="*50)
    mode_names = {0: 'Standard', 1: 'High Noise', 2: 'Severely Degraded'}
    print(f"Mode {mode}: {mode_names.get(mode, 'Unknown')}")
    
    venv_python = voicefixer_dir / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("[SKIP] VoiceFixer not found")
        return False
    
    cmd = [str(venv_python), "-c", f"""
import sys
sys.path.insert(0, '{voicefixer_dir}')
sys.path.insert(0, '{voicefixer_dir}/voicefixer')

from voicefixer import VoiceFixer
vf = VoiceFixer()
vf.restore('{input_file}', '{output_file}', cuda=False, mode={mode})
print('Processing complete!')
"""]
    
    try:
        print("Processing...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(voicefixer_dir))
        
        if result.returncode == 0:
            print("[SUCCESS] Audio enhancement complete!")
            return True
        else:
            if mode == 2:
                print("[WARNING] Mode 2 failed. Retrying with Mode 0...")
                return run_voicefixer_direct(input_file, output_file, voicefixer_dir, 0)
            print(f"[ERROR] VoiceFixer failed")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def process_audio(input_file, mode, script_dir, voicefixer_dir, demucs_venv=None):
    input_path = Path(input_file).resolve()
    
    # 出力ファイル名
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_name = f"{timestamp}__{input_path.stem}_cleaned.wav"
    output_path = input_path.parent / output_name
    
    print(f"\nInput: {input_path.name}")
    print(f"Output: {output_name}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp1 = temp_path / "temp_demucs.wav"
        temp2 = temp_path / "temp_audiosep.wav"
        temp3 = temp_path / "temp_sepformer.wav"
        temp_denoised = temp_path / "temp_denoised.wav"
        
        current_file = input_path
        
        # Mode selection
        if mode == "M":
            # Demucs-only BGM removal pipeline (practical version)
            print("\n[Demucs BGM Removal Mode] ⭐RECOMMENDED⭐")
            print("High-quality vocal extraction using Demucs")
            
            if not demucs_venv:
                print("[ERROR] Demucs venv path not provided")
                return None
            
            # Demucs vocal extraction
            demucs_result = run_demucs(str(current_file), str(output_path), demucs_venv)
            if demucs_result:
                print(f"[SUCCESS] BGM removed, vocals extracted")
                print(f"[INFO] Output size: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")
                return output_path
            else:
                print("[ERROR] Demucs processing failed")
                return None
            
        elif mode == "D":
            # Denoiser only
            print("\n[Denoiser Only Mode]")
            result = run_denoiser(str(input_path), str(output_path), script_dir)
            return output_path if result else None
        
        elif mode == "R":
            # Resemble Enhance - Denoise Only (高速)
            print("\n[Resemble Enhance - Denoise Mode]")
            print("SE・ノイズ・拍手などを除去します（高速モード）")
            success = run_resemble_enhance(str(input_path), str(output_path), script_dir, "denoise")
            return output_path if success else None
        
        elif mode == "E":
            # Resemble Enhance - Denoise + Enhance (高品質)
            print("\n[Resemble Enhance - Full Enhancement Mode]")
            print("SE・ノイズ除去 + 音質向上（高品質モード）")
            success = run_resemble_enhance(str(input_path), str(output_path), script_dir, "enhance")
            return output_path if success else None
            
        else:
            # Standard pipeline: Denoiser → VoiceFixer
            print("\n[Standard Pipeline]")
            
            # Denoiser
            denoised = run_denoiser(str(input_path), str(temp1), script_dir)
            if denoised and temp1.exists():
                current_file = temp1
            
            # VoiceFixer
            mode_int = int(mode)
            success = run_voicefixer_direct(str(current_file), str(output_path), voicefixer_dir, mode_int)
            
            if not success and current_file != input_path:
                shutil.copy(current_file, output_path)
                print("\n[INFO] Saved Denoiser result only")
                return output_path
            
            return output_path if success else None

# メイン処理
if len(sys.argv) > 3:
    input_file = sys.argv[1]
    mode = sys.argv[2]
    script_dir = Path(sys.argv[3])
    voicefixer_dir = Path(sys.argv[4]) if len(sys.argv) > 4 else Path.home() / "voicefixer_app"
    demucs_venv = sys.argv[5] if len(sys.argv) > 5 else None
    
    result = process_audio(input_file, mode, script_dir, voicefixer_dir, demucs_venv)
    if result:
        print(f"\n✅ Processing complete!")
        print(f"📁 Saved to: {result}")
    else:
        print("\n❌ Processing failed")
else:
    print("Error: Missing required arguments")
PYTHON_SCRIPT

# 最初のファイル入力
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Drag & Drop Audio File Here  ${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "File: " input_file
input_file=$(echo "$input_file" | sed "s/^'//" | sed "s/'$//" | sed 's/^"//' | sed 's/"$//')

if [ -z "$input_file" ] || [ ! -f "$input_file" ]; then
    echo -e "${RED}[ERROR] File not found${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

# メインループ
while true; do
    echo ""
    echo -e "${CYAN}━━━ Select Mode ━━━${NC}"
    echo -e "${GREEN}0${NC}: Standard (Denoiser + VoiceFixer)"
    echo -e "${YELLOW}1${NC}: High Noise (Aggressive)"
    echo -e "${RED}2${NC}: Severely Degraded"
    echo ""
    echo -e "${CYAN}━━━ Advanced Modes ━━━${NC}"
    echo -e "${BLUE}M${NC}: BGM Removal (Demucs High-Quality Vocal Extraction)"
    echo -e "    Best for: Music/BGM removal, podcast with intro/outro"
    echo -e "${BLUE}D${NC}: Denoiser Only (Basic noise reduction)"
    echo ""
    echo -e "${CYAN}━━━ Resemble Enhance (SE/Noise Removal) ━━━${NC}"
    echo -e "${GREEN}R${NC}: Resemble Denoise (SE/Noise removal, Fast) ⭐ RECOMMENDED"
    echo -e "    Best for: 効果音(SE)・拍手・歓声・環境音の除去"
    echo -e "${YELLOW}E${NC}: Resemble Enhance (Denoise + Quality boost)"
    echo -e "    Best for: 高品質なノイズ除去 + 音声強化"
    echo ""
    echo -e "${PURPLE}F${NC}: Select Different File"
    echo -e "${PURPLE}Q${NC}: Quit"
    echo ""
    read -p "Select [Enter=0]: " mode
    mode=${mode:-0}
    
    # 終了チェック
    if [[ "$mode" =~ ^[Qq]$ ]]; then
        echo -e "${GREEN}Goodbye!${NC}"
        break
    fi
    
    # ファイル変更
    if [[ "$mode" =~ ^[Ff]$ ]]; then
        echo ""
        echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  Drag & Drop New Audio File  ${NC}"
        echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        read -p "File: " new_file
        new_file=$(echo "$new_file" | sed "s/^'//" | sed "s/'$//" | sed 's/^"//' | sed 's/"$//')
        
        if [ -n "$new_file" ] && [ -f "$new_file" ]; then
            input_file="$new_file"
            echo -e "${GREEN}File changed!${NC}"
        else
            echo -e "${YELLOW}[WARNING] File not found. Using previous file${NC}"
        fi
        continue
    fi
    
    # Mode検証
    if ! [[ "$mode" =~ ^[0-2MmDdRrEe]$ ]]; then
        echo -e "${YELLOW}[WARNING] Invalid mode. Please try again${NC}"
        continue
    fi
    
    # 大文字に変換
    mode=$(echo "$mode" | tr '[:lower:]' '[:upper:]')
    
    echo ""
    echo -e "${GREEN}━━━ Processing Started! ━━━${NC}"
    echo -e "File: ${BLUE}$(basename "$input_file")${NC}"
    
    # Demucs venvパスを探す（Mモードで必要）
    DEMUCS_VENV=""
    if [[ "$mode" =~ ^[Mm]$ ]]; then
        # 一般的なDemucsインストール場所を探す
        if [ -d "$HOME/demucs_venv310" ]; then
            DEMUCS_VENV="$HOME/demucs_venv310"
            echo -e "${GREEN}[INFO] Found Demucs at: $DEMUCS_VENV${NC}"
        elif [ -d "$HOME/demucs_venv" ]; then
            DEMUCS_VENV="$HOME/demucs_venv"
            echo -e "${GREEN}[INFO] Found Demucs at: $DEMUCS_VENV${NC}"
        elif [ -d "$HOME/.demucs" ]; then
            DEMUCS_VENV="$HOME/.demucs"
            echo -e "${GREEN}[INFO] Found Demucs at: $DEMUCS_VENV${NC}"
        elif command -v demucs &> /dev/null; then
            # demucsコマンドがシステムにある場合
            DEMUCS_PATH=$(which demucs)
            # venvのパスを推測
            DEMUCS_VENV=$(dirname $(dirname "$DEMUCS_PATH"))
            echo -e "${GREEN}[INFO] Found Demucs at: $DEMUCS_VENV${NC}"
        else
            echo -e "${RED}[ERROR] Demucs not found. Please install Demucs first.${NC}"
            echo -e "${YELLOW}Install command:${NC}"
            echo -e "${YELLOW}  python3 -m venv ~/demucs_venv${NC}"
            echo -e "${YELLOW}  source ~/demucs_venv/bin/activate${NC}"
            echo -e "${YELLOW}  pip install demucs${NC}"
            continue
        fi
    fi
    
    # Python実行
    python3 /tmp/audio_cleaner_pro.py "$input_file" "$mode" "$PROJECT_DIR" "$HOME/voicefixer_app" "$DEMUCS_VENV"
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Continue processing?${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # 再生オプション（Macの場合）
    if command -v afplay &> /dev/null; then
        echo ""
        read -p "Play processed audio? [y/N]: " play_audio
        if [[ "$play_audio" =~ ^[Yy]$ ]]; then
            latest_file=$(ls -t "$(dirname "$input_file")"/*__*_cleaned.wav 2>/dev/null | head -1)
            if [ -f "$latest_file" ]; then
                echo -e "${GREEN}Playing... (Ctrl+C to stop)${NC}"
                afplay "$latest_file"
            fi
        fi
    fi
done

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}    AudioCleaner PRO - Goodbye!      ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 一時ファイル削除
rm -f /tmp/audio_cleaner_pro.py

