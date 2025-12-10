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
echo -e "${CYAN}║    AudioCleaner v1.1                 ║${NC}"
echo -e "${CYAN}║    AI-Powered Audio Enhancement      ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Pythonスクリプトを直接埋め込み
cat > /tmp/audio_cleaner_main.py << 'PYTHON_SCRIPT'
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
    
    denoiser_venv = denoiser_dir / "venv" / "bin" / "python"
    denoiser_script = denoiser_dir / "scripts" / "run_clearSound.py"
    
    if not denoiser_venv.exists():
        print("[SKIP] Denoiser not found")
        print(f"Expected path: {denoiser_venv}")
        return None
    
    if not denoiser_script.exists():
        print("[SKIP] Denoiser script not found")
        print(f"Expected path: {denoiser_script}")
        return None
    
    cmd = [str(denoiser_venv), str(denoiser_script), input_file, "-o", output_file, "-q", "high"]
    
    try:
        print("Processing...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(denoiser_dir))
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
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

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
    print("Step 2: VoiceFixer - Audio Enhancement")
    print("="*50)
    mode_names = {0: 'Standard', 1: 'High Noise', 2: 'Severely Degraded'}
    print(f"Mode {mode}: {mode_names.get(mode, 'Unknown')}")
    
    venv_python = voicefixer_dir / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("[SKIP] VoiceFixer not found")
        print(f"Expected path: {venv_python}")
        return False
    
    # VoiceFixerを直接実行
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
            print(f"[ERROR] VoiceFixer failed (exit code: {result.returncode})")
            if result.stdout:
                print(f"[STDOUT]\n{result.stdout}")
            if result.stderr:
                print(f"[STDERR]\n{result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_audio(input_file, mode, denoiser_dir, voicefixer_dir):
    input_path = Path(input_file).resolve()
    
    # 出力ファイル名
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_name = f"{timestamp}__{input_path.stem}_cleaned.wav"
    output_path = input_path.parent / output_name
    
    print(f"\nInput: {input_path.name}")
    print(f"Output: {output_name}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        denoised_file = temp_path / "temp_denoised.wav"
        
        if mode == "D":
            # Denoiserのみ
            print("\n[Denoiser Only Mode]")
            result = run_denoiser(str(input_path), str(output_path), denoiser_dir)
            return output_path if result else None
        elif mode == "R":
            # Resemble Enhance - Denoise Only (高速)
            print("\n[Resemble Enhance - Denoise Mode]")
            success = run_resemble_enhance(str(input_path), str(output_path), denoiser_dir, "denoise")
            return output_path if success else None
        elif mode == "E":
            # Resemble Enhance - Denoise + Enhance (高品質)
            print("\n[Resemble Enhance - Full Enhancement Mode]")
            success = run_resemble_enhance(str(input_path), str(output_path), denoiser_dir, "enhance")
            return output_path if success else None
        else:
            # 両方実行
            current_file = input_path
            
            # Denoiser
            denoised = run_denoiser(str(input_path), str(denoised_file), denoiser_dir)
            if denoised and denoised_file.exists():
                current_file = denoised_file
            
            # VoiceFixer
            mode_int = int(mode)
            success = run_voicefixer_direct(str(current_file), str(output_path), voicefixer_dir, mode_int)
            
            if not success and current_file != input_path:
                # VoiceFixer失敗時、Denoiserの結果を保存
                shutil.copy(current_file, output_path)
                print("\n[INFO] Saved Denoiser result only")
                return output_path
            
            return output_path if success else None

# メイン処理
if len(sys.argv) > 3:
    input_file = sys.argv[1]
    mode = sys.argv[2]
    denoiser_dir = Path(sys.argv[3])
    voicefixer_dir = Path(sys.argv[4]) if len(sys.argv) > 4 else Path.home() / "voicefixer_app"
    
    result = process_audio(input_file, mode, denoiser_dir, voicefixer_dir)
    if result:
        print(f"\n✅ Processing complete!")
        print(f"📁 Saved to: {result}")
    else:
        print("\n❌ Processing failed")
else:
    print("Error: Missing required arguments")
    print("Usage: script.py <input_file> <mode> <denoiser_dir> [voicefixer_dir]")
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
    echo -e "${GREEN}0${NC}: Standard (Recommended)"
    echo -e "${YELLOW}1${NC}: High Noise"
    echo -e "${RED}2${NC}: Severely Degraded"
    echo -e "${BLUE}D${NC}: Denoiser Only"
    echo -e "${CYAN}━━━ Resemble Enhance (SE/Noise Removal) ━━━${NC}"
    echo -e "${GREEN}R${NC}: Resemble Denoise (SE/Noise removal, Fast)"
    echo -e "${YELLOW}E${NC}: Resemble Enhance (Denoise + Quality boost)"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
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
    if ! [[ "$mode" =~ ^[0-2DdRrEe]$ ]]; then
        echo -e "${YELLOW}[WARNING] Invalid mode. Please try again${NC}"
        continue
    fi
    
    # 大文字に変換
    mode=$(echo "$mode" | tr '[:lower:]' '[:upper:]')
    
    echo ""
    echo -e "${GREEN}━━━ Processing Started! ━━━${NC}"
    echo -e "File: ${BLUE}$(basename "$input_file")${NC}"
    
    # Python実行
    python3 /tmp/audio_cleaner_main.py "$input_file" "$mode" "$PROJECT_DIR" "$HOME/voicefixer_app"
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Continue processing?${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # 再生オプション（Macの場合）
    if command -v afplay &> /dev/null; then
        echo ""
        read -p "Play processed audio? [y/N]: " play_audio
        if [[ "$play_audio" =~ ^[Yy]$ ]]; then
            # 最新の出力ファイルを探す
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
echo -e "${GREEN}    AudioCleaner - Goodbye!         ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 一時ファイル削除
rm -f /tmp/audio_cleaner_main.py

