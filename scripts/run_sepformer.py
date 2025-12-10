#!/usr/bin/env python3
"""
SepFormer-DNS Integration Script
Post-processing enhancement for cleaned audio
"""

import os
import sys
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def setup_sepformer():
    """Setup SepFormer-DNS model"""
    try:
        import torch
        import torchaudio
        # Use the updated inference API
        from speechbrain.inference.separation import SepformerSeparation as Separator
    except ImportError as e:
        print(f"[エラー] SpeechBrainが見つかりません: {e}")
        print("インストール方法:")
        print("  pip install 'speechbrain>=0.5.16'")
        print("  pip install 'torchaudio<2.9.0'  # TorchAudio 2.9+は互換性問題あり")
        sys.exit(1)
    
    try:
        # Check TorchAudio version
        import torchaudio
        ta_version = torchaudio.__version__
        major, minor = map(int, ta_version.split('.')[:2])
        if major > 2 or (major == 2 and minor >= 9):
            print(f"[警告] TorchAudio {ta_version} は互換性問題がある可能性があります")
            print("[警告] TorchAudio < 2.9 の使用を推奨します")
        
        # Initialize SepFormer-DNS model
        device = "cpu"  # CPU for stability
        print(f"[情報] デバイス: {device}")
        
        # Get script directory for model cache
        script_dir = Path(__file__).parent.parent
        savedir = script_dir / "pretrained_models" / "sepformer-dns4"
        savedir.mkdir(parents=True, exist_ok=True)
        
        print("[情報] SepFormer-DNSモデル読み込み中...")
        model = Separator.from_hparams(
            source="speechbrain/sepformer-dns4-16k-enhancement",
            savedir=str(savedir),
            run_opts={"device": device}
        )
        
        return model
    except Exception as e:
        print(f"[エラー] モデル読み込み失敗: {e}")
        print("初回実行時はモデルのダウンロードに時間がかかります")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def enhance_audio(input_path, output_path, model):
    """
    Enhance audio quality using SepFormer-DNS
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        model: SepFormer model
    """
    try:
        import torch
        import torchaudio
        
        print(f"[処理中] {input_path} を読み込み中...")
        
        # Load audio
        waveform, sr = torchaudio.load(input_path)
        print(f"[情報] 元の音声: {sr}Hz, {waveform.shape[0]}ch")
        
        # Resample to 16kHz (SepFormer-DNS requirement)
        target_sr = 16000
        if sr != target_sr:
            print(f"[情報] リサンプリング中 ({sr}Hz → {target_sr}Hz)...")
            resampler = torchaudio.transforms.Resample(sr, target_sr)
            waveform = resampler(waveform)
        
        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            print("[情報] ステレオ→モノラル変換中...")
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        print("[情報] 音質向上処理中...")
        
        # Enhance using SepFormer
        # Model expects (batch, time) format
        waveform_batch = waveform.unsqueeze(0)  # Add batch dimension
        
        with torch.no_grad():
            enhanced = model.separate_batch(waveform_batch)
        
        # Extract enhanced audio (remove batch dimension)
        if isinstance(enhanced, tuple):
            enhanced = enhanced[0]
        
        # Ensure correct shape
        if enhanced.dim() == 3:
            enhanced = enhanced.squeeze(0)
        elif enhanced.dim() == 1:
            enhanced = enhanced.unsqueeze(0)
        
        print(f"[保存中] {output_path} に保存中...")
        torchaudio.save(output_path, enhanced.cpu(), target_sr)
        
        print("[完了] 音質向上完了！")
        return True
        
    except Exception as e:
        print(f"[エラー] 処理中にエラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description="SepFormer-DNS - Audio Enhancement"
    )
    parser.add_argument("input", nargs="?", help="入力音声ファイル")
    parser.add_argument("-o", "--output", help="出力ファイル名")
    
    args = parser.parse_args()
    
    if not args.input:
        print("===== SepFormer-DNS - Audio Enhancement =====")
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
        output_path = input_path.parent / f"{input_path.stem}_enhanced{input_path.suffix}"
    
    print(f"入力: {input_path}")
    print(f"出力: {output_path}")
    print("")
    
    model = setup_sepformer()
    success = enhance_audio(str(input_path), str(output_path), model)
    
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

