#!/usr/bin/env python3
"""
MP-SENet - High Quality Speech Enhancement Script
高品質音声強調: magnitude/phaseを並列処理してノイズを除去

MP-SENetは音声強調（Speech Enhancement）に特化したモデルで、
magnitude と phase スペクトルを並列で推定・処理することで、
従来手法より高品質なノイズ除去を実現します。

PESQ スコア: 3.50 (VoiceBank+DEMAND dataset)
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
        device = "cuda"
        print("[情報] CUDA GPU使用")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        # MPSは一部の操作で問題が発生する可能性があるため、CPUを推奨
        device = "cpu"
        print("[情報] CPU使用 (MPS利用可能だが安定性のためCPU使用)")
    else:
        device = "cpu"
        print("[情報] CPU使用")
    
    return device


def setup_mp_senet(device="cpu"):
    """MP-SENetモデルのセットアップ"""
    try:
        from MPSENet import MPSENet
    except ImportError as e:
        print(f"[エラー] MPSENetが見つかりません: {e}")
        print("インストール方法:")
        print("  pip install MPSENet")
        sys.exit(1)
    
    try:
        print("[情報] MP-SENetモデル読み込み中...")
        # 事前学習済みモデルをHugging Face Hubからロード
        model = MPSENet.from_pretrained("JacobLinCool/MP-SENet-DNS").to(device)
        model.eval()
        print("[情報] モデル読み込み完了")
        return model
    except Exception as e:
        print(f"[エラー] モデル読み込み失敗: {e}")
        print("初回実行時はモデルのダウンロードに時間がかかります")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def load_audio(input_path):
    """音声ファイルを読み込み"""
    import torch
    import torchaudio
    
    print(f"[処理中] {input_path} を読み込み中...")
    waveform, sr = torchaudio.load(input_path)
    print(f"[情報] 元の音声: {sr}Hz, {waveform.shape[0]}ch, {waveform.shape[1]/sr:.2f}秒")
    
    return waveform, sr


def resample_audio(waveform, sr, target_sr=16000):
    """サンプリングレートを変換（MP-SENetは16kHz推奨）"""
    import torchaudio
    
    if sr != target_sr:
        print(f"[情報] リサンプリング中 ({sr}Hz -> {target_sr}Hz)...")
        resampler = torchaudio.transforms.Resample(sr, target_sr)
        waveform = resampler(waveform)
    
    return waveform, target_sr


def process_with_mp_senet(waveform, sr, model, device="cpu"):
    """
    MP-SENetで音声を処理
    
    Args:
        waveform: 入力波形 (torch.Tensor)
        sr: サンプリングレート
        model: MP-SENetモデル
        device: 処理デバイス
    
    Returns:
        処理後の波形とサンプリングレート
    """
    import torch
    
    # MP-SENetは16kHzで動作
    target_sr = 16000
    original_sr = sr
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
        ch_wav = waveform[ch].unsqueeze(0).to(device)  # (1, time)
        
        print(f"[処理中] MP-SENet音声強調中{'...' if not is_stereo else ''}")
        
        with torch.no_grad():
            # MP-SENetで処理
            enhanced_wav = model(ch_wav)
        
        # 結果を取得
        if isinstance(enhanced_wav, tuple):
            enhanced_wav = enhanced_wav[0]
        
        processed_channels.append(enhanced_wav.squeeze().cpu())
    
    # チャンネルを結合
    if is_stereo:
        output_wav = torch.stack(processed_channels, dim=0)
    else:
        output_wav = processed_channels[0].unsqueeze(0)
    
    return output_wav, target_sr


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


def process_audio(input_path, output_path):
    """
    メイン処理関数
    
    Args:
        input_path: 入力ファイルパス
        output_path: 出力ファイルパス
    """
    try:
        # デバイスセットアップ
        device = setup_device()
        
        # モデルセットアップ
        model = setup_mp_senet(device)
        
        # 音声読み込み
        waveform, sr = load_audio(input_path)
        
        # MP-SENetで処理
        output_wav, output_sr = process_with_mp_senet(waveform, sr, model, device)
        
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
        description="MP-SENet - 高品質音声強調ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  基本的な使い方:
    python run_mp_senet.py input.wav
    
  出力ファイル指定:
    python run_mp_senet.py input.wav -o output.wav

特徴:
  - magnitude/phase を並列処理
  - PESQ スコア 3.50 達成
  - ノイズの多い音声のクリーンアップに最適
"""
    )
    parser.add_argument("input", nargs="?", help="入力音声ファイル")
    parser.add_argument("-o", "--output", help="出力ファイル名")
    
    args = parser.parse_args()
    
    # 対話モード
    if not args.input:
        print("===== MP-SENet - 高品質音声強調ツール =====")
        print("")
        print("このツールは高品質なノイズ除去を行います:")
        print("  - 背景ノイズ")
        print("  - 環境音")
        print("  - ホワイトノイズ")
        print("")
        print("特徴:")
        print("  - magnitude/phase 並列処理")
        print("  - PESQ スコア 3.50")
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
        output_path = input_path.parent / f"{input_path.stem}_mp_senet.wav"
    
    print(f"入力: {input_path}")
    print(f"出力: {output_path}")
    print("")
    
    success = process_audio(str(input_path), str(output_path))
    
    if success:
        print(f"\n結果ファイル: {output_path}")
        print("完了!")
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
