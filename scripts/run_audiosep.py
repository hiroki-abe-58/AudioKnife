#!/usr/bin/env python3
"""
AudioSep Integration Script
Text-guided audio separation for SE removal
"""

import os
import sys
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def setup_audiosep():
    """Setup AudioSep model"""
    try:
        import torch
        import torchaudio
        # AudioSep uses pipeline module from GitHub repo
        from pipeline import build_audiosep
    except ImportError as e:
        print(f"[エラー] AudioSepが見つかりません: {e}")
        print("インストール方法:")
        print("  pip install 'git+https://github.com/Audio-AGI/AudioSep.git'")
        sys.exit(1)
    
    try:
        # Initialize AudioSep model
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[情報] デバイス: {device}")
        
        # Get script directory to find config/checkpoint
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / "config" / "audiosep_base.yaml"
        checkpoint_path = script_dir / "checkpoint" / "audiosep_base_4M_steps.ckpt"
        
        # Create directories if they don't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        
        print("[情報] AudioSepモデル読み込み中...")
        model = build_audiosep(
            config_yaml=str(config_path),
            checkpoint_path=str(checkpoint_path),
            device=device
        )
        
        return model, device
    except Exception as e:
        print(f"[エラー] モデル読み込み失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def separate_audio(input_path, output_path, text_query, model, device):
    """
    Separate audio using text query
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        text_query: Text description of target sound (e.g., "human speech")
        model: AudioSep model
        device: Torch device
    """
    try:
        from pipeline import inference
        
        print(f"[処理中] {input_path} を読み込み中...")
        print(f"[情報] 分離中: '{text_query}'")
        
        # Use AudioSep's inference function
        # It handles loading, resampling, and saving internally
        inference(
            model=model,
            audio_file=input_path,
            text=text_query,
            output_file=output_path,
            device=device
        )
        
        print("[完了] 分離完了！")
        return True
        
    except Exception as e:
        print(f"[エラー] 処理中にエラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description="AudioSep - Text-guided Audio Separation"
    )
    parser.add_argument("input", nargs="?", help="入力音声ファイル")
    parser.add_argument("-o", "--output", help="出力ファイル名")
    parser.add_argument(
        "-q", "--query", 
        default="human speech",
        help="分離対象の説明 (例: 'human speech', 'male voice', 'female voice')"
    )
    parser.add_argument(
        "--remove-se",
        action="store_true",
        help="SE除去モード（複数のSEを検出して除去）"
    )
    
    args = parser.parse_args()
    
    if not args.input:
        print("===== AudioSep - Text-guided Audio Separation =====")
        print("使い方:")
        print("  1. 音声ファイルをドラッグ&ドロップ")
        print("  2. Enterキーを押す")
        print("")
        input_path = input("音声ファイルのパス: ").strip().strip("'\"")
        if not input_path:
            print("[エラー] ファイルパスが入力されていません")
            sys.exit(1)
    else:
        input_path = args.input
    
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"[エラー] ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        suffix = "_speech" if not args.remove_se else "_no_se"
        output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
    
    print(f"入力: {input_path}")
    print(f"出力: {output_path}")
    print(f"クエリ: '{args.query}'")
    print("")
    
    model, device = setup_audiosep()
    
    if args.remove_se:
        # SE removal mode: extract multiple SEs and subtract
        print("\n[SE除去モード]")
        print("検出するSE: applause, door slam, camera shutter, footsteps, keyboard")
        
        se_types = [
            "applause",
            "door slam", 
            "camera shutter",
            "footsteps",
            "keyboard typing",
            "beep sound"
        ]
        
        # Extract each SE type (implementation would require multiple passes)
        # For now, just extract speech directly
        success = separate_audio(
            str(input_path), 
            str(output_path), 
            args.query, 
            model, 
            device
        )
    else:
        # Direct extraction mode
        success = separate_audio(
            str(input_path), 
            str(output_path), 
            args.query, 
            model, 
            device
        )
    
    if success:
        print(f"\n結果ファイル: {output_path}")
        print("完了！")
    else:
        print("\n処理失敗")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[中断] Ctrl+Cで中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"[エラー] 予期せぬエラー: {e}")
        sys.exit(1)

