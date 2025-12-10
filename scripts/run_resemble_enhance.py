#!/usr/bin/env python3
"""
Resemble Enhance - Audio Denoising and Enhancement Script
SE・ノイズ・拍手などを分離し、クリアな音声を抽出

Resemble Enhanceを使用して:
1. Denoiser: 背景ノイズ、環境音、SEなどを除去
2. Enhancer: 音質を向上（オプション）
"""

import os
import sys
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def setup_device():
    """デバイスのセットアップ"""
    import torch
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("[情報] CUDA GPU使用")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        # MPSは一部の操作で問題が発生する可能性があるため、CPUを推奨
        device = torch.device("cpu")
        print("[情報] CPU使用 (MPS利用可能だが安定性のためCPU使用)")
    else:
        device = torch.device("cpu")
        print("[情報] CPU使用")
    
    return device


def load_audio(input_path):
    """音声ファイルを読み込み"""
    import torch
    import torchaudio
    
    print(f"[処理中] {input_path} を読み込み中...")
    waveform, sr = torchaudio.load(input_path)
    print(f"[情報] 元の音声: {sr}Hz, {waveform.shape[0]}ch, {waveform.shape[1]/sr:.2f}秒")
    
    return waveform, sr


def resample_audio(waveform, sr, target_sr=44100):
    """サンプリングレートを変換"""
    import torchaudio
    
    if sr != target_sr:
        print(f"[情報] リサンプリング中 ({sr}Hz -> {target_sr}Hz)...")
        resampler = torchaudio.transforms.Resample(sr, target_sr)
        waveform = resampler(waveform)
    
    return waveform, target_sr


def process_with_resemble_enhance(waveform, sr, device, mode="denoise", nfe=32, solver="midpoint", lambd=0.5, tau=0.5):
    """
    Resemble Enhanceで音声を処理
    
    Args:
        waveform: 入力波形 (torch.Tensor)
        sr: サンプリングレート
        device: 処理デバイス
        mode: "denoise" (ノイズ除去のみ) or "enhance" (ノイズ除去+音質向上)
        nfe: Number of function evaluations (Enhancer用、デフォルト32)
        solver: ソルバー ("midpoint", "rk4", "euler")
        lambd: Enhancer強度パラメータ (0.0-1.0)
        tau: Enhancer時間パラメータ (0.0-1.0)
    
    Returns:
        処理後の波形とサンプリングレート
    """
    import torch
    from resemble_enhance.enhancer.inference import denoise, enhance
    
    # Resemble Enhanceは44.1kHzで動作
    target_sr = 44100
    waveform, sr = resample_audio(waveform, sr, target_sr)
    
    # モノラルに変換（ステレオの場合は各チャンネルを処理）
    is_stereo = waveform.shape[0] > 1
    processed_channels = []
    
    if is_stereo:
        print("[情報] ステレオ音声を検出、各チャンネル個別処理...")
    
    for ch in range(waveform.shape[0]):
        if is_stereo:
            print(f"  - チャンネル {ch+1} 処理中...")
        
        # チャンネルデータを取得
        ch_wav = waveform[ch].to(device)
        
        # Step 1: Denoising
        print(f"[処理中] ノイズ除去中{'...' if not is_stereo else ''}")
        denoised_wav, new_sr = denoise(ch_wav, sr, device)
        
        if mode == "enhance":
            # Step 2: Enhancement (オプション)
            print(f"[処理中] 音質向上中 (nfe={nfe}, solver={solver})...")
            enhanced_wav, new_sr = enhance(
                denoised_wav, 
                new_sr, 
                device, 
                nfe=nfe,
                solver=solver,
                lambd=lambd,
                tau=tau
            )
            processed_channels.append(enhanced_wav.cpu())
        else:
            processed_channels.append(denoised_wav.cpu())
    
    # チャンネルを結合
    if is_stereo:
        output_wav = torch.stack(processed_channels, dim=0)
    else:
        output_wav = processed_channels[0].unsqueeze(0)
    
    return output_wav, new_sr


def save_audio(waveform, sr, output_path):
    """音声ファイルを保存"""
    import torchaudio
    
    print(f"[保存中] {output_path} に保存中...")
    
    # 正規化（クリッピング防止）
    max_val = waveform.abs().max()
    if max_val > 1.0:
        waveform = waveform / max_val * 0.99
    
    torchaudio.save(output_path, waveform, sr)
    print(f"[情報] 出力: {sr}Hz, {waveform.shape[0]}ch")


def process_audio(input_path, output_path, mode="denoise", nfe=32, solver="midpoint", lambd=0.5, tau=0.5):
    """
    メイン処理関数
    
    Args:
        input_path: 入力ファイルパス
        output_path: 出力ファイルパス
        mode: "denoise" or "enhance"
        nfe: Number of function evaluations (Enhancer用)
        solver: ソルバー
        lambd: Enhancer強度
        tau: Enhancer時間パラメータ
    """
    try:
        # デバイスセットアップ
        device = setup_device()
        
        # 音声読み込み
        waveform, sr = load_audio(input_path)
        
        # Resemble Enhanceで処理
        output_wav, output_sr = process_with_resemble_enhance(
            waveform, sr, device, 
            mode=mode,
            nfe=nfe,
            solver=solver,
            lambd=lambd,
            tau=tau
        )
        
        # 保存
        save_audio(output_wav, output_sr, output_path)
        
        print("[完了] 処理完了!")
        return True
        
    except Exception as e:
        print(f"[エラー] 処理中にエラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Resemble Enhance - SE・ノイズ除去ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  ノイズ除去のみ（高速、推奨）:
    python run_resemble_enhance.py input.wav -m denoise
    
  ノイズ除去 + 音質向上（高品質だが遅い）:
    python run_resemble_enhance.py input.wav -m enhance
    
  音質向上のパラメータ調整:
    python run_resemble_enhance.py input.wav -m enhance --nfe 64 --lambd 0.7
"""
    )
    parser.add_argument("input", nargs="?", help="入力音声ファイル")
    parser.add_argument("-o", "--output", help="出力ファイル名")
    parser.add_argument("-m", "--mode", choices=["denoise", "enhance"], default="denoise",
                       help="処理モード: denoise=ノイズ除去のみ, enhance=ノイズ除去+音質向上 (デフォルト: denoise)")
    parser.add_argument("--nfe", type=int, default=32,
                       help="Enhancerのステップ数 (デフォルト: 32、高い値=高品質だが遅い)")
    parser.add_argument("--solver", choices=["midpoint", "rk4", "euler"], default="midpoint",
                       help="Enhancerのソルバー (デフォルト: midpoint)")
    parser.add_argument("--lambd", type=float, default=0.5,
                       help="Enhancer強度 0.0-1.0 (デフォルト: 0.5)")
    parser.add_argument("--tau", type=float, default=0.5,
                       help="Enhancer時間パラメータ 0.0-1.0 (デフォルト: 0.5)")
    
    args = parser.parse_args()
    
    # 対話モード
    if not args.input:
        print("===== Resemble Enhance - SE・ノイズ除去ツール =====")
        print("")
        print("このツールは音声から以下を除去します:")
        print("  - 背景ノイズ（ホワイトノイズ、環境音）")
        print("  - SE（効果音）")
        print("  - 拍手・歓声")
        print("  - その他の非音声成分")
        print("")
        print("使い方:")
        print("  1. 音声ファイルをこのウィンドウにドラッグ&ドロップ")
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
    
    # 出力パス
    if args.output:
        output_path = Path(args.output)
    else:
        suffix = "_denoised" if args.mode == "denoise" else "_enhanced"
        output_path = input_path.parent / f"{input_path.stem}{suffix}.wav"
    
    print(f"入力: {input_path}")
    print(f"出力: {output_path}")
    print(f"モード: {'ノイズ除去のみ' if args.mode == 'denoise' else 'ノイズ除去+音質向上'}")
    if args.mode == "enhance":
        print(f"  - NFE: {args.nfe}")
        print(f"  - Solver: {args.solver}")
        print(f"  - Lambda: {args.lambd}")
        print(f"  - Tau: {args.tau}")
    print("")
    
    success = process_audio(
        str(input_path), 
        str(output_path),
        mode=args.mode,
        nfe=args.nfe,
        solver=args.solver,
        lambd=args.lambd,
        tau=args.tau
    )
    
    if success:
        print(f"\n結果ファイル: {output_path}")
        print("おつかれさん!")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


